# RAGShield entry point.
# Replace the import below with your own RAG application's answer function.

from rag_app import answer
from app.cli import main

if __name__ == "__main__":
    main(answer)
