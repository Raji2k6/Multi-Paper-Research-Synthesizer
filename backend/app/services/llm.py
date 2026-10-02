import logging

from openai import OpenAI
from openai import OpenAIError

from app.core.config import settings


logger = logging.getLogger(__name__)


class LLMGenerationError(RuntimeError):
    """The configured language-model provider could not generate an answer."""


def uses_openrouter() -> bool:
    backend = settings.LLM_BACKEND.lower()
    if backend == "auto":
        return bool(settings.OPENROUTER_API_KEY)
    if backend == "local":
        return False
    if backend == "openrouter" and settings.OPENROUTER_API_KEY:
        return True
    raise ValueError(
        "LLM_BACKEND must be 'auto' or 'local', or 'openrouter' with an API key."
    )


def _generate(prompt: str, model: str, timeout: float = 60) -> str:
    client = OpenAI(
        api_key=settings.OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        timeout=timeout,
    )
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
    except OpenAIError as error:
        logger.exception("Language-model provider request failed.")
        raise LLMGenerationError(
            "The language-model provider request failed."
        ) from error

    choices = getattr(response, "choices", None)
    if not choices:
        logger.warning("Language-model provider returned no completion choices.")
        raise LLMGenerationError(
            "The language-model provider returned no completion choices."
        )

    message = getattr(choices[0], "message", None)
    answer = getattr(message, "content", None)
    if not isinstance(answer, str) or not answer.strip():
        logger.warning("Language-model provider returned an empty completion.")
        raise LLMGenerationError(
            "The language-model provider returned an empty completion."
        )
    return answer.strip()


def _evidence_fallback(context: str, *, synthesis: bool) -> str:
    if synthesis:
        return (
            "## Retrieved paper-wise evidence\n\n"
            f"{context}\n\n"
            "---\n"
            "The hosted language-model provider did not return a usable "
            "comparison. No findings or contradictions have been inferred; "
            "the cited excerpts above are the evidence retrieved for this question."
        )

    return (
        "## Retrieved evidence\n\n"
        f"{context}\n\n"
        "---\n"
        "The hosted language-model provider did not return a usable answer. "
        "These are the retrieved paper excerpts; use their paper and page "
        "labels as citations."
    )


def generate_answer(question: str, context: str) -> str:
    """
    Generate a grounded answer, or return retrieved evidence in offline mode.
    """
    if not uses_openrouter():
        return _evidence_fallback(context, synthesis=False).replace(
            "The hosted language-model provider did not return a usable answer. ",
            "Hosted language-model generation is disabled. ",
        )

    prompt = f"""
Answer the question using ONLY the supplied research-paper context.
If it is insufficient, say so. Distinguish papers and cite page labels.
Do not invent facts, citations, or conclusions.

Research-paper context:
{context}

Question: {question}
"""
    try:
        return _generate(prompt, settings.OPENROUTER_MODEL)
    except LLMGenerationError:
        logger.warning("Returning retrieved evidence because chat generation failed.")
        return _evidence_fallback(context, synthesis=False)


def generate_synthesis(question: str, paper_context: str) -> str:
    """
    Compare papers using supplied evidence, with an explicit offline mode.
    """
    if not uses_openrouter():
        return _evidence_fallback(paper_context, synthesis=True).replace(
            "The hosted language-model provider did not return a usable comparison. ",
            "Hosted language-model generation is disabled. ",
        )

    prompt = f"""
Compare the research papers using ONLY the supplied evidence. Do not use outside
knowledge or invent claims. Distinguish a difference from a contradiction;
only identify contradictions when the claims are incompatible. Include paper
and page citations, common findings, differences, contradictions, evidence gaps,
and an overall synthesis.

Paper evidence:
{paper_context}

Question: {question}
"""
    try:
        return _generate(
            prompt,
            settings.OPENROUTER_SYNTHESIS_MODEL,
            timeout=60,
        )
    except LLMGenerationError:
        logger.warning("Returning retrieved evidence because synthesis generation failed.")
        return _evidence_fallback(paper_context, synthesis=True)


def generate_evidence_comparison(question: str, paper_context: str) -> str:
    return generate_synthesis(question, paper_context)
