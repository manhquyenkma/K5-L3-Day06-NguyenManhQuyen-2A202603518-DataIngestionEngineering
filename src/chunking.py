"""Implement fixed-size and structure-aware chunking strategies."""
import re
from .models import Chunk, DocumentPage


def fixed_size(page: DocumentPage, size: int = 500, overlap: int = 50) -> list[Chunk]:
    """Split text into overlapping windows and retain page metadata.
    
    Strategy A: Mechanical character sliding window.
    """
    text = page.text
    if not text:
        return []

    stride = max(1, size - overlap)
    chunks: list[Chunk] = []
    start = 0
    idx = 0

    while start < len(text):
        end = min(start + size, len(text))
        chunk_text = text[start:end].strip()

        if chunk_text:
            chunk_meta = dict(page.metadata)
            chunk_meta.update({
                "strategy": "fixed_size",
                "chunk_index": idx,
                "start_char": start,
                "end_char": end,
                "char_len": len(chunk_text),
            })
            chunks.append(
                Chunk(
                    chunk_id=f"A_{page.document_id}_p{page.page}_c{idx}",
                    document_id=page.document_id,
                    source=page.source,
                    page=page.page,
                    text=chunk_text,
                    metadata=chunk_meta,
                )
            )
            idx += 1

        if end >= len(text):
            break
        start += stride

    return chunks


def _split_into_sentences(text: str) -> list[str]:
    """Split text into sentence/clause units."""
    # Split by period/semicolon followed by space or newline, or list item indicators
    parts = re.split(r"(?<=[.;\n])\s+", text)
    return [p.strip() for p in parts if p.strip()]


def by_paragraph(page: DocumentPage, max_size: int = 800) -> list[Chunk]:
    """Group paragraphs, split oversized paragraphs cleanly, retain metadata.
    
    Strategy B / C: Structural & semantic chunking preserving complete clauses.
    """
    text = page.text
    if not text:
        return []

    # Identify structural blocks: split on blank lines or article/clause boundaries
    # Keep ĐIỀU headers and paragraphs together where possible
    raw_paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    
    merged_blocks: list[str] = []
    current_block: list[str] = []
    current_len = 0

    for para in raw_paragraphs:
        para_len = len(para)
        
        # If single paragraph is oversized, break it down by sentences
        if para_len > max_size:
            # First flush any pending accumulated block
            if current_block:
                merged_blocks.append("\n\n".join(current_block))
                current_block = []
                current_len = 0
            
            # Sub-split oversized paragraph by sentence units
            sentences = _split_into_sentences(para)
            sub_block: list[str] = []
            sub_len = 0
            for sent in sentences:
                if sub_len + len(sent) + 1 > max_size and sub_block:
                    merged_blocks.append(" ".join(sub_block))
                    sub_block = [sent]
                    sub_len = len(sent)
                else:
                    sub_block.append(sent)
                    sub_len += len(sent) + 1
            if sub_block:
                merged_blocks.append(" ".join(sub_block))
        else:
            # Check if adding this paragraph exceeds max_size
            if current_len + para_len + 2 > max_size and current_block:
                merged_blocks.append("\n\n".join(current_block))
                current_block = [para]
                current_len = para_len
            else:
                current_block.append(para)
                current_len += para_len + 2

    if current_block:
        merged_blocks.append("\n\n".join(current_block))

    # Build Chunk objects
    chunks: list[Chunk] = []
    for idx, block_text in enumerate(merged_blocks):
        chunk_meta = dict(page.metadata)
        chunk_meta.update({
            "strategy": "structural_paragraph",
            "chunk_index": idx,
            "char_len": len(block_text),
        })
        chunks.append(
            Chunk(
                chunk_id=f"B_{page.document_id}_p{page.page}_c{idx}",
                document_id=page.document_id,
                source=page.source,
                page=page.page,
                text=block_text,
                metadata=chunk_meta,
            )
        )

    return chunks
