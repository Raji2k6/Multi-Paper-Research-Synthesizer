from openai import OpenAI

from app.core.config import settings


client = OpenAI(
    api_key=settings.OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)


def generate_answer(question: str, context: str) -> str:
    """
    Generate an answer using the retrieved research-paper context.
    """

    prompt = f"""
You are an AI Research Assistant for a multi-paper research system.

Answer the user's question using ONLY the information provided
in the research-paper context.

Rules:
1. Do not use information that is not present in the context.
2. If the context does not contain enough information to answer,
   say:
   "I couldn't find the answer in the uploaded research papers."
3. When information comes from different documents, clearly
   distinguish between them.
4. Do not invent facts, citations, or conclusions.

Research-paper context:
--------------------------------
{context}
--------------------------------

Question:
{question}

Answer:
"""

    response = client.chat.completions.create(
    model="qwen/qwen3.8-27b:free",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ],
    temperature=0.2
    )

    print("========== OPENROUTER RESPONSE ==========")
    print(response)
    print("=========================================")

    return response.choices[0].message.content

def generate_synthesis(question: str, paper_context: str) -> str:
    """
    Generate a synthesis across multiple research papers.
    """

    prompt = f"""
You are an AI Research Assistant specializing in multi-paper research analysis.

The user has uploaded multiple research papers.

Your task is to answer the question by comparing the information
provided from each paper.

IMPORTANT RULES:

1. Use ONLY the information provided in the paper context.
2. Do not introduce outside knowledge.
3. Do not invent claims.
4. Clearly distinguish information from different papers.
5. Identify common points between papers.
6. Identify meaningful differences between papers.
7. Only call something a contradiction if the papers actually
   make conflicting claims.
8. If there is no contradiction, explicitly say:
   "No contradiction was identified in the retrieved evidence."
9. Include page numbers when referring to information from a paper.

Structure your response as:

## Paper-wise Findings

### Paper 1
...

### Paper 2
...

## Common Points
...

## Differences
...

## Contradictions
...

## Overall Synthesis
...

Research Paper Context:
--------------------------------
{paper_context}
--------------------------------

Question:
{question}

Answer:
"""

    response = client.chat.completions.create(
        model="nvidia/nemotron-3-ultra-550b-a55b:free",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
        timeout=60
    )

    return response.choices[0].message.content


def generate_evidence_comparison(
    question: str,
    paper_context: str
) -> str:
    """
    Compare evidence across papers and identify
    common points, differences, and actual contradictions.
    """

    prompt = f"""
You are an AI research comparison assistant.

You are given evidence retrieved from multiple research papers.

Your task is to compare the papers strictly using the
provided evidence.

IMPORTANT RULES:

1. Use ONLY the supplied paper evidence.
2. Do not use outside knowledge.
3. Do not invent facts or claims.
4. Every important claim must be traceable to a paper and page.
5. A difference is NOT automatically a contradiction.
6. Different terminology does NOT constitute a contradiction.
7. Different levels of detail do NOT constitute a contradiction.
8. A contradiction requires two papers to make incompatible
   claims about the same subject.
9. If the evidence does not establish a contradiction,
   explicitly say that no contradiction was identified.
10. If evidence is insufficient, say so instead of guessing.

For each paper:

- Identify the claims relevant to the question.
- Include the page number.
- Keep the claim faithful to the source.

Then compare the claims.

Use this structure:

## Paper-wise Evidence

### Paper 1
- Claim
- Page

### Paper 2
- Claim
- Page

## Common Points

List claims supported by multiple papers.

## Differences

List differences in:
- terminology
- emphasis
- scope
- level of detail
- approach

Do NOT call these contradictions unless the claims conflict.

## Contradiction Analysis

For each possible contradiction:

### Candidate
- Paper 1 claim:
- Paper 2 claim:
- Analysis:
- Contradiction: Yes/No
- Evidence:

If there are no actual contradictions:

"No contradiction was identified in the retrieved evidence."

## Evidence Gaps

Identify anything that cannot be determined from
the retrieved evidence.

## Overall Synthesis

Provide a concise synthesis based only on the evidence.

Research Paper Evidence:
--------------------------------
{paper_context}
--------------------------------

Question:
{question}

Answer:
"""

    response = client.chat.completions.create(
        model="nvidia/nemotron-3-ultra-550b-a55b:free",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1,
        timeout=60
    )

    return response.choices[0].message.content