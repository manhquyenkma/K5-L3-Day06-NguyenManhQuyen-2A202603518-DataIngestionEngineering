"""Evaluate retrieved evidence and preserve per-query traces."""
import re
from typing import Any


def clean_str(s: str) -> str:
    """Normalize string for robust evidence match comparison."""
    s = s.lower().replace("\n", " ").replace("\r", " ")
    return re.sub(r"\s+", " ", s).strip()


def check_evidence_match(chunk_text: str, evidence_quote: str) -> bool:
    """Check if the chunk contains the required gold evidence.
    
    Checks exact match first; if split by minor punctuation/whitespace,
    checks normalized string containment.
    """
    if evidence_quote in chunk_text:
        return True
    
    c_norm = clean_str(chunk_text)
    e_norm = clean_str(evidence_quote)
    if e_norm in c_norm:
        return True

    # Check key informative clauses if quote is multi-line
    parts = [p.strip() for p in evidence_quote.split("\n") if len(p.strip()) > 15]
    if parts:
        all_parts_found = all(clean_str(p) in c_norm for p in parts)
        if all_parts_found:
            return True

    return False


def is_evidence_hit(hit: dict[str, Any], question: dict[str, Any]) -> tuple[bool, str]:
    """Determine if a single hit qualifies as a valid gold evidence hit."""
    gold_page = question["gold_page"]
    hit_page = hit.get("page")
    
    # 1. Page verification
    if hit_page != gold_page:
        return False, f"Page mismatch: retrieved p{hit_page} vs gold p{gold_page}"
    
    # 2. Evidence verification
    has_evidence = check_evidence_match(hit.get("text", ""), question["evidence_quote"])
    if not has_evidence:
        return False, "Evidence quote not found in chunk text"

    return True, "Valid evidence hit"


def evaluate_query(question: dict[str, Any], hits: list[dict[str, Any]]) -> dict[str, Any]:
    """Check source/page and gold evidence; keep hit@1, hit@3 trace and filter audit."""
    hit_results = []
    for rank, h in enumerate(hits, start=1):
        hit_ok, reason = is_evidence_hit(h, question)
        hit_results.append({
            "rank": rank,
            "chunk_id": h.get("chunk_id"),
            "page": h.get("page"),
            "section": h.get("section"),
            "score": h.get("score"),
            "is_hit": hit_ok,
            "reason": reason,
            "text_snippet": h.get("text", "")[:150] + "..." if len(h.get("text", "")) > 150 else h.get("text", "")
        })

    hit_at_1 = len(hit_results) > 0 and hit_results[0]["is_hit"]
    hit_at_3 = any(hr["is_hit"] for hr in hit_results[:3])
    hit_ranks = [hr["rank"] for hr in hit_results if hr["is_hit"]]

    # Filter compliance audit
    q_filter = question.get("filter")
    filter_compliant = True
    if q_filter:
        for h in hits:
            for k, expected_v in q_filter.items():
                if h.get(k) != expected_v and h.get("metadata", {}).get(k) != expected_v:
                    filter_compliant = False

    trace = {
        "question_id": question["id"],
        "split": question["split"],
        "type": question.get("type", "general"),
        "question": question["question"],
        "expected_answer": question["expected_answer"],
        "gold_page": question["gold_page"],
        "evidence_quote": question["evidence_quote"],
        "filter": q_filter,
        "hit_at_1": hit_at_1,
        "hit_at_3": hit_at_3,
        "hit_ranks": hit_ranks,
        "filter_compliant": filter_compliant if q_filter else None,
        "top_hits": hit_results
    }
    return trace


def summarize(traces: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate Hit@1 and Evidence Hit@3 by dev/test split."""
    splits = ["all", "dev", "test"]
    summary = {}

    for s in splits:
        if s == "all":
            sub_traces = traces
        else:
            sub_traces = [t for t in traces if t["split"] == s]

        n = len(sub_traces)
        if n == 0:
            continue

        h1_count = sum(1 for t in sub_traces if t["hit_at_1"])
        h3_count = sum(1 for t in sub_traces if t["hit_at_3"])

        # Filter compliance
        filter_traces = [t for t in sub_traces if t.get("filter") is not None]
        filter_comp_count = sum(1 for t in filter_traces if t.get("filter_compliant") is True)
        filter_rate_str = f"{filter_comp_count}/{len(filter_traces)}" if filter_traces else "N/A"

        summary[s] = {
            "total_questions": n,
            "hit_at_1_count": h1_count,
            "hit_at_1_ratio": f"{h1_count}/{n}",
            "hit_at_1_percent": round(h1_count / n * 100, 2),
            "hit_at_3_count": h3_count,
            "hit_at_3_ratio": f"{h3_count}/{n}",
            "hit_at_3_percent": round(h3_count / n * 100, 2),
            "filter_compliance": filter_rate_str
        }

    return summary
