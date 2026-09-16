import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DB_CONNECTION = os.getenv("PGVECTOR_CONNECTION")
JUDGE_MODEL = os.getenv("DEEPEVAL_MODEL", "gemini-3.5-flash-lite")
RATE_LIMIT = int(os.getenv("DEEPEVAL_RATE_LIMIT", "12"))

TEST_FILE = BASE_DIR / "tests" / "rag_tests.json"
SECURITY_FILE = BASE_DIR / "tests" / "security_tests.json"
REPORT_DIR = BASE_DIR / "reports"
REPORT_DIR.mkdir(exist_ok=True)

RESPONSE_FILE = REPORT_DIR / "response.json"
EVAL_FILE = REPORT_DIR / "report.json"
SECURITY_REPORT_FILE = REPORT_DIR / "security_results.json"
FINAL_REPORT_FILE = REPORT_DIR / "ragshield_report.json"



os.environ.setdefault("DEEPEVAL_RETRY_MAX_ATTEMPTS", "6")
os.environ.setdefault("DEEPEVAL_RETRY_INITIAL_SECONDS", "10")
os.environ.setdefault("DEEPEVAL_RETRY_EXP_BASE", "2")
os.environ.setdefault("DEEPEVAL_RETRY_CAP_SECONDS", "90")
os.environ.setdefault("DEEPEVAL_PER_TASK_TIMEOUT_SECONDS_OVERRIDE", "600")
os.environ.setdefault("DEEPEVAL_TASK_GATHER_BUFFER_SECONDS_OVERRIDE", "30")
