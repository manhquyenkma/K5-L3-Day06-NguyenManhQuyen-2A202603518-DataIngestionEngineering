"""Read and normalize source data with full source-to-chunk traceability."""
import json
import unicodedata
import re
from pathlib import Path
from .models import DocumentPage


def normalize_text(text: str) -> str:
    """Normalize Unicode (NFC) and whitespace while preserving useful paragraph structure."""
    if not text:
        return ""
    # Canonical Unicode NFC normalization
    text = unicodedata.normalize("NFC", text)
    # Normalize line endings to \n
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Replace non-breaking spaces and tabs with regular spaces
    text = text.replace("\u00a0", " ").replace("\t", " ")
    # Replace multiple spaces within a line with single space
    lines = [re.sub(r" +", " ", line).strip() for line in text.split("\n")]
    # Collapse 3 or more newlines into 2 (keep paragraph breaks)
    normalized = "\n".join(lines)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized).strip()
    return normalized


def load_corpus(path: Path | str, document_id: str = "so-tay-sinh-vien-2024") -> list[DocumentPage]:
    """Load JSON/text corpus into normalized DocumentPage instances."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Corpus file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    pages: list[DocumentPage] = []
    empty_pages = []

    for item in data:
        raw_text = item.get("text", "")
        cleaned_text = normalize_text(raw_text)
        page_num = item.get("page", 0)

        if not cleaned_text:
            empty_pages.append(page_num)
            continue

        metadata = {
            "section": item.get("section", "general"),
            "title": item.get("title", ""),
            "year": item.get("year", 2024),
            "char_count": len(cleaned_text),
        }

        doc_page = DocumentPage(
            document_id=document_id,
            source=str(file_path).replace("\\", "/"),
            page=page_num,
            text=cleaned_text,
            metadata=metadata
        )
        pages.append(doc_page)

    if empty_pages:
        print(f"Warning: Pages {empty_pages} had no text and were skipped.")

    return pages


def load_pdf(path: Path, document_id: str, source: str) -> list[DocumentPage]:
    """Extract physical pages from PDF; keep page numbers, source and error logs."""
    try:
        import pypdf
    except ImportError:
        raise ImportError("pypdf is required to extract PDF files.")

    reader = pypdf.PdfReader(str(path))
    pages: list[DocumentPage] = []
    empty_pages = []

    for idx, page in enumerate(reader.pages, start=1):
        raw_text = page.extract_text() or ""
        cleaned = normalize_text(raw_text)
        if not cleaned:
            empty_pages.append(idx)
            continue

        pages.append(
            DocumentPage(
                document_id=document_id,
                source=source,
                page=idx,
                text=cleaned,
                metadata={"page_number": idx}
            )
        )

    if empty_pages:
        print(f"Warning: PDF pages {empty_pages} contained no extractable text.")

    return pages
