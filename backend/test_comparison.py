from app.core.database import SessionLocal

from app.services.retrieval import (
    retrieve_relevant_chunks_per_document,
    group_chunks_by_document,
    build_paper_context
)

from app.services.comparison import compare_papers


def main():

    db = SessionLocal()

    try:

        question = "Compare how the uploaded papers describe the Spiral Model."

        chunks = retrieve_relevant_chunks_per_document(
            db=db,
            question=question,
            chunks_per_document=3,
            candidate_k=10,
            max_distance=0.75
        )

        print("\nRetrieved evidence:")
        print("=" * 80)

        for chunk in chunks:

            print(
                f"\nDocument: {chunk.document_id}"
            )

            print(
                f"Title: {chunk.document_title}"
            )

            print(
                f"Page: {chunk.page_number}"
            )

            print(
                f"Distance: {chunk.distance}"
            )

        grouped_documents = group_chunks_by_document(
            chunks
        )

        paper_context = build_paper_context(
            grouped_documents
        )

        print("\n\nGenerating evidence-grounded comparison...")
        print("=" * 80)

        answer = compare_papers(
            question=question,
            paper_context=paper_context
        )

        print("\n")
        print(answer)

    finally:

        db.close()


if __name__ == "__main__":
    main()