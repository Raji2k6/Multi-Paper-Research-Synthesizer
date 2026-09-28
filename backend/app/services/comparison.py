from app.services.llm import generate_evidence_comparison


def compare_papers(
    question: str,
    paper_context: str
) -> str:
    """
    Compare multiple papers using evidence-grounded analysis.
    """

    return generate_evidence_comparison(
        question=question,
        paper_context=paper_context
    )