from app.services.llm import generate_synthesis


def synthesize_papers(question: str, paper_context: str) -> str:
    """
    Generate a multi-paper synthesis using the structured paper context.
    """

    return generate_synthesis(
        question=question,
        paper_context=paper_context
    )