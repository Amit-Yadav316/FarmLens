from __future__ import annotations

import sys

from farmlens.core.config import get_settings
from farmlens.features.rag.ingestion import PDFIngestion


def main(pdf_dir: str = "./data/pdfs") -> None:
    """Ingest all PDFs in a directory into ChromaDB."""
    settings = get_settings()
    ingestion = PDFIngestion(settings)
    count = ingestion.run(pdf_dir)
    print(f"Ingested {count} chunks from {pdf_dir}")


if __name__ == "__main__":
    directory = sys.argv[1] if len(sys.argv) > 1 else "./data/pdfs"
    main(directory)
