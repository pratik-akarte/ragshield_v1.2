"""
DEVELOPER RAG ADAPTER

Replace this example with your existing RAG application.

RAGShield only requires:
    answer(question) -> dict

Recommended response:
{
    "answer": "...",
    "context": "...",
    "citations": "..."
}

A plain string is also supported.
"""


def answer(question: str):
    # TODO: Connect your existing RAG chain here.
    # Example:
    #
    # response = chain.invoke(question)
    # return {
    #     "answer": response.answer,
    #     "context": response.context,
    #     "citations": response.citations,
    # }

    return {
        "answer": f"Demo response for: {question}",
        "context": "Demo context",
        "citations": "demo",
    }
