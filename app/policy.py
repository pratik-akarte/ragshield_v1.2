import json
import yaml
from datetime import datetime

from .config import FINAL_REPORT_FILE


def check_policy(quality, security, policy_file="policy.yaml"):
    with open(policy_file, encoding="utf-8") as f:
        thresholds = yaml.safe_load(f)["thresholds"]

    total = len(security)
    attack_failures = sum(not x["blocked"] for x in security)
    pii_leaks = sum(x["pii_detected"] for x in security)

    checks = {
        "faithfulness": quality.get("Faithfulness", {}).get("average_score", 0)
            >= thresholds["faithfulness_min"],
        "contextual_precision": quality.get("Contextual Precision", {}).get("average_score", 0)
            >= thresholds["contextual_precision_min"],
        "answer_correctness": quality.get("Answer Correctness", {}).get("average_score", 0)
            >= thresholds["answer_correctness_min"],
        "attack_success_rate": (attack_failures / total if total else 0)
            <= thresholds["attack_success_rate_max"],
        "pii_leakage_rate": (pii_leaks / total if total else 0)
            <= thresholds["pii_leakage_rate_max"],
    }

    report = {
        "project": "RAGShield",
        "quality": quality,
        "security": {
            "total_attacks": total,
            "successful_attacks": attack_failures,
            "pii_leaks": pii_leaks,
        },
        "checks": checks,
        "overall": "PASS" if all(checks.values()) else "FAIL",
        "timestamp": datetime.now().isoformat(),
    }

    FINAL_REPORT_FILE.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )
    return report
