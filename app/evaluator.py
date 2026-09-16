import asyncio
import json
import os
import threading
import time
from collections import defaultdict, deque
from statistics import mean

from deepeval import evaluate
from deepeval.evaluate import AsyncConfig, CacheConfig
from deepeval.metrics import ContextualPrecisionMetric, FaithfulnessMetric, GEval
from deepeval.models import GeminiModel
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

from .cache import load_cache, save_cache, cache_key
from .config import (
    GOOGLE_API_KEY, JUDGE_MODEL, RATE_LIMIT,
    TEST_FILE, RESPONSE_FILE, EVAL_FILE,
)


class RateLimiter:
    """Sliding-window rate limiter. Core behavior kept from the original."""

    def __init__(self, max_calls=12, period=60.0):
        self.max_calls = max_calls
        self.period = period
        self.calls = deque()
        self._lock = threading.Lock()
        self._alock = asyncio.Lock()

    def _wait_time(self):
        now = time.monotonic()
        while self.calls and now - self.calls[0] > self.period:
            self.calls.popleft()

        if len(self.calls) >= self.max_calls:
            return self.period - (now - self.calls[0])
        return 0.0

    def acquire(self):
        with self._lock:
            while (wait := self._wait_time()) > 0:
                time.sleep(wait)
            self.calls.append(time.monotonic())

    async def a_acquire(self):
        async with self._alock:
            while (wait := self._wait_time()) > 0:
                await asyncio.sleep(wait)
            self.calls.append(time.monotonic())


class RateLimitedGeminiModel(GeminiModel):
    def __init__(self, *args, limiter=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.limiter = limiter or RateLimiter()

    def generate(self, *args, **kwargs):
        self.limiter.acquire()
        return super().generate(*args, **kwargs)

    async def a_generate(self, *args, **kwargs):
        await self.limiter.a_acquire()
        return await super().a_generate(*args, **kwargs)


def run_rag_tests(rag):
    tests = json.loads(TEST_FILE.read_text(encoding="utf-8"))
    cache = load_cache()
    results = []

    for test in tests:
        question = test["question"]
        key = cache_key(question)

        if key in cache:
            print(f"⚡ Cached: {question}")
            response = cache[key]
        else:
            print(f"🤖 Testing: {question}")
            response = rag.ask(question)
            cache[key] = response
            save_cache(cache)
            time.sleep(2)

        results.append({
            "question": question,
            "expected_answer": test.get("expected_answer"),
            "expected_source": test.get("expected_source"),
            "response": response,
        })

    RESPONSE_FILE.write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return results


def run_deepeval(records):
    limiter = RateLimiter(max_calls=RATE_LIMIT)

    judge = RateLimitedGeminiModel(
        model=JUDGE_MODEL,
        api_key=GOOGLE_API_KEY,
        temperature=0,
        limiter=limiter,
    )

    test_cases = [
        LLMTestCase(
            input=r["question"],
            actual_output=r["response"]["answer"],
            retrieval_context=[r["response"]["context"]],
            expected_output=r.get("expected_answer"),
        )
        for r in records
    ]

    metrics = [
        FaithfulnessMetric(model=judge, threshold=0.5),
        ContextualPrecisionMetric(model=judge, threshold=0.5),
        GEval(
            name="Answer Correctness",
            criteria=(
                "Determine whether the actual output is factually correct "
                "and semantically equivalent to the expected output. "
                "Penalize missing or contradictory facts; do not penalize "
                "differences in phrasing."
            ),
            evaluation_params=[
                LLMTestCaseParams.ACTUAL_OUTPUT,
                LLMTestCaseParams.EXPECTED_OUTPUT,
            ],
            model=judge,
            threshold=0.5,
        ),
    ]

    async_cfg = AsyncConfig(max_concurrent=1, throttle_value=1)

    def execute(use_cache):
        return evaluate(
            test_cases=test_cases,
            metrics=metrics,
            async_config=async_cfg,
            cache_config=CacheConfig(
                use_cache=use_cache,
                write_cache=use_cache,
            ),
        )

    try:
        result = execute(True)
    except AttributeError as e:
        if any(k in str(e) for k in ("get_cached_api_test_case", "test_cases_lookup_map")):
            print("⚠️ Stale DeepEval cache detected. Clearing and retrying...")
            for filename in (".deepeval-cache.json", ".temp-deepeval-cache.json"):
                if os.path.exists(filename):
                    os.remove(filename)
            result = execute(False)
        else:
            raise

    scores = defaultdict(list)
    for test in result.test_results:
        for metric in test.metrics_data:
            scores[metric.name].append(metric.score)

    summary = {
        name: {"average_score": round(mean(values), 4), "n": len(values)}
        for name, values in scores.items()
    }

    EVAL_FILE.write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )
    return summary
