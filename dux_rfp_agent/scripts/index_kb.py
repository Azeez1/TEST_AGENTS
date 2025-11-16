#!/usr/bin/env python3
"""
Knowledge base indexing script.
Index documents into Pinecone for retrieval during proposal generation.
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dux_rfp_agent.ingestion import DocumentIngestion
from dux_rfp_agent.logger import logger
from dux_rfp_agent.retrieval import KnowledgeBaseRetrieval


def index_documents(
    input_dir: Path,
    namespace: str = "default",
    doc_type: str = "other",
    sector: str = "government",
    batch_size: int = 10,
):
    """
    Index documents from directory into Pinecone.

    Args:
        input_dir: Directory containing documents
        namespace: Pinecone namespace
        doc_type: Document type (resume, past_performance, etc.)
        sector: Industry sector
        batch_size: Batch size for processing
    """
    logger.info(f"Indexing documents from: {input_dir}")
    logger.info(f"Namespace: {namespace}, Type: {doc_type}, Sector: {sector}")

    # Initialize components
    ingestion = DocumentIngestion()
    kb = KnowledgeBaseRetrieval(enabled=True)

    if not kb.enabled:
        logger.error("Knowledge base not available - check Pinecone configuration")
        sys.exit(1)

    # Find all documents
    supported_extensions = [".pdf", ".docx", ".txt"]
    doc_files = []

    for ext in supported_extensions:
        doc_files.extend(input_dir.glob(f"**/*{ext}"))

    logger.info(f"Found {len(doc_files)} documents to index")

    if not doc_files:
        logger.warning("No documents found")
        return

    # Process documents
    documents = []

    for i, doc_path in enumerate(doc_files, 1):
        logger.info(f"Processing {i}/{len(doc_files)}: {doc_path.name}")

        try:
            # Ingest document
            doc_data = ingestion.ingest(doc_path)

            # Create document chunks for indexing
            # Each page or section becomes a separate vector
            for page_num, page_text in doc_data["pages"].items():
                if len(page_text.strip()) < 100:
                    continue  # Skip very short pages

                doc_id = f"{doc_path.stem}_p{page_num}"

                # Build metadata
                metadata = {
                    "doc_id": doc_id,
                    "doc_type": doc_type,
                    "content_type": "section",
                    "title": doc_data["metadata"].get("title", doc_path.stem),
                    "source_file": doc_path.name,
                    "page_range": str(page_num),
                    "sector": [sector],
                    "classification": "internal",
                }

                documents.append({"id": doc_id, "text": page_text, "metadata": metadata})

        except Exception as e:
            logger.error(f"Failed to process {doc_path}: {e}")
            continue

    logger.info(f"Prepared {len(documents)} document chunks for indexing")

    # Index in batches
    try:
        total_indexed = kb.upsert(documents, namespace=namespace, batch_size=batch_size)
        logger.info(f"Successfully indexed {total_indexed} documents to namespace '{namespace}'")

    except Exception as e:
        logger.error(f"Indexing failed: {e}", exc_info=True)
        sys.exit(1)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Index knowledge base documents into Pinecone",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Index resumes
  python scripts/index_kb.py --input ./kb/resumes --type resume --sector government

  # Index past performance
  python scripts/index_kb.py --input ./kb/past_performance --type past_performance

  # Index to custom namespace
  python scripts/index_kb.py --input ./kb/docs --namespace custom_ns
        """,
    )

    parser.add_argument(
        "--input", type=str, required=True, help="Directory containing documents to index"
    )

    parser.add_argument(
        "--type",
        type=str,
        default="other",
        choices=[
            "resume",
            "past_performance",
            "case_study",
            "technical_writeup",
            "boilerplate",
            "company_info",
            "capability_statement",
            "certification",
            "other",
        ],
        help="Document type",
    )

    parser.add_argument(
        "--sector",
        type=str,
        default="government",
        choices=["government", "healthcare", "finance", "education", "energy", "other"],
        help="Industry sector",
    )

    parser.add_argument(
        "--namespace", type=str, default="default", help="Pinecone namespace (default: default)"
    )

    parser.add_argument(
        "--batch-size", type=int, default=10, help="Batch size for indexing (default: 10)"
    )

    args = parser.parse_args()

    # Validate input directory
    input_dir = Path(args.input)
    if not input_dir.exists():
        logger.error(f"Input directory not found: {input_dir}")
        sys.exit(1)

    # Run indexing
    try:
        index_documents(
            input_dir=input_dir,
            namespace=args.namespace,
            doc_type=args.type,
            sector=args.sector,
            batch_size=args.batch_size,
        )

    except KeyboardInterrupt:
        logger.info("Indexing interrupted by user")
        sys.exit(130)


if __name__ == "__main__":
    main()
