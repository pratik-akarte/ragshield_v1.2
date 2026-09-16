from .adapter import RAGAdapter
from .evaluator import run_rag_tests, run_deepeval
from .security import run_security_tests
from .policy import check_policy


def main(rag_app):
    rag = RAGAdapter(rag_app)

    print("\n🛡️ RAGShield\n")

    print("1/4 RAG tests...")
    records = run_rag_tests(rag)

    print("2/4 DeepEval...")
    quality = run_deepeval(records)
    print(f"DeepEval: {quality}")

    print("3/4 Security tests...")
    security = run_security_tests(rag)
    print(f"Security: {len(security)} attacks tested")

    print("4/4 Policy...")
    report = check_policy(quality, security)

    print("\n" + "-" * 35)
    for name, passed in report["checks"].items():
        print(f"{'✅' if passed else '❌'} {name}")
    print("-" * 35)
    print(f"\nRAGShield: {report['overall']}")

    return report
