"""Audit script to perform manual assessment and extract data for the 5 dimensions."""
import json
from pathlib import Path

# Load traces
with open("results/retrieval_trace.json", "r", encoding="utf-8") as f:
    traces = json.load(f)

# Load corpus
with open("data/so_tay_sinh_vien_2024.json", "r", encoding="utf-8") as f:
    corpus = json.load(f)

corpus_by_page = {p["page"]: p for p in corpus}

print("=" * 60)
print("AUDIT DIMENSION 2: CHUNK COHERENCE ON 10 POSITIONS (PAGES 1-10)")
print("=" * 60)

# Inspect chunks for pages 1 to 10 in Strategy A and Strategy B
# Load chunks from Qdrant or generate them
from src.chunking import fixed_size, by_paragraph
from src.models import DocumentPage

pages_1_to_10 = [
    DocumentPage(
        document_id="so-tay-sinh-vien-2024",
        source="data/so_tay_sinh_vien_2024.json",
        page=p["page"],
        text=p["text"],
        metadata={"section": p["section"], "title": p["title"]}
    ) for p in corpus[:10]
]

coherence_audit = []
for p in pages_1_to_10:
    p_num = p.page
    chunks_a = fixed_size(p, size=500, overlap=50)
    chunks_b = by_paragraph(p, max_size=800)
    
    # We audit the first chunk of each page
    c_a = chunks_a[0].text
    c_b = chunks_b[0].text
    
    coherence_audit.append({
        "page": p_num,
        "title": p.metadata["title"],
        "chunk_a": c_a,
        "chunk_a_len": len(c_a),
        "chunk_b": c_b,
        "chunk_b_len": len(c_b),
    })

with open("results/coherence_audit_raw.json", "w", encoding="utf-8") as f:
    json.dump(coherence_audit, f, ensure_ascii=False, indent=2)

print(f"Extracted {len(coherence_audit)} positions for coherence audit.")

print("\n" + "=" * 60)
print("AUDIT DIMENSION 3 & 4: TEST QUESTIONS (q16-q20) ACROSS STRATEGIES")
print("=" * 60)

test_audit = {}
for strat in ["strategy_a", "strategy_b", "strategy_c"]:
    strat_traces = [t for t in traces[strat] if t["split"] == "test"]
    test_audit[strat] = strat_traces

with open("results/test_audit_raw.json", "w", encoding="utf-8") as f:
    json.dump(test_audit, f, ensure_ascii=False, indent=2)

for strat, t_list in test_audit.items():
    print(f"\n--- {strat.upper()} ---")
    for t in t_list:
        print(f"Q: {t['question_id']} | Gold p{t['gold_page']} | Hit@1: {t['hit_at_1']} | Hit@3: {t['hit_at_3']}")
        for h in t["top_hits"]:
            print(f"   Rank {h['rank']}: p{h['page']} (score={h['score']:.4f}, hit={h['is_hit']}) - {h['reason']}")

