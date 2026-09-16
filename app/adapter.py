class RAGAdapter:
    """Small adapter that lets RAGShield test any RAG application."""

    def __init__(self, rag_app):
        self.rag_app = rag_app

    def ask(self, question: str) -> dict:
        response = self.rag_app(question)

        if isinstance(response, str):
            return {"answer": response, "context": "", "citations": ""}

        return {
            "answer": response.get("answer", ""),
            "context": response.get("context", ""),
            "citations": response.get("citations", ""),
        }
