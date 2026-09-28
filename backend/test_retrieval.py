from app.core.database import SessionLocal
from app.services.retrieval import (
    retrieve_relevant_chunks,
    group_chunks_by_document,
    build_paper_context,
    retrieve_chunks_per_document,
    retrieve_relevant_chunks_per_document
)

def main():

    db = SessionLocal()

    try:
        question = "What is Spiral model?"

        chunks = retrieve_relevant_chunks(
            db=db,
            question=question,
            top_k=5
        )

        grouped = group_chunks_by_document(chunks)

        paper_context = build_paper_context(grouped)

        print("\n\nPaper-wise Context:")
        print("=" * 80)
        print(paper_context)

        print("\n\nGrouped by document:")
        print("=" * 80)

        for document in grouped:
            print("\nDocument ID:", document["document_id"])
            print("Document Title:", document["document_title"])
            print("Filename:", document["filename"])

            for chunk in document["chunks"]:
                print(
                    f"  Page: {chunk['page']} | "
                    f"Distance: {chunk['distance']}"
            )

        print("\nQuestion:")
        print(question)

        print("\nRetrieved chunks:")
        print("=" * 80)

        for i, chunk in enumerate(chunks, start=1):

            print(f"\nResult {i}")
            print("-" * 80)

            print("Chunk ID:", chunk.id)
            print("Document ID:", chunk.document_id)
            print("Document Title:", chunk.document_title)
            print("Filename:", chunk.document_filename)
            print("Page:", chunk.page_number)
            print("Distance:", chunk.distance)

            print("\nContent:")
            print(chunk.content[:500])


        print("\n\nBalanced Multi-Paper Retrieval:")
        print("=" * 80)

        balanced_chunks = retrieve_chunks_per_document(
            db=db,
            question=question,
            chunks_per_document=3
        )

        for i, chunk in enumerate(balanced_chunks, start=1):

            print(f"\nResult {i}")
            print("-" * 80)

            print("Chunk ID:", chunk.id)
            print("Document ID:", chunk.document_id)
            print("Document Title:", chunk.document_title)
            print("Page:", chunk.page_number)
            print("Distance:", chunk.distance)

            print("\nContent:")
            print(chunk.content[:300])

        print("\n\nRelevance-Aware Multi-Paper Retrieval:")
        print("=" * 80)

        relevant_chunks = retrieve_relevant_chunks_per_document(
            db=db,
            question=question,
            chunks_per_document=3,
            candidate_k=10,
            max_distance=0.75
        )

        for i, chunk in enumerate(
            relevant_chunks,
            start=1
        ):
            print(f"\nResult {i}")
            print("-" * 80)

            print("Chunk ID:", chunk.id)
            print("Document ID:", chunk.document_id)
            print("Document Title:", chunk.document_title)
            print("Page:", chunk.page_number)
            print("Distance:", chunk.distance)

            print("\nContent:")
            print(chunk.content[:300])

    finally:
        db.close()


if __name__ == "__main__":
    main()