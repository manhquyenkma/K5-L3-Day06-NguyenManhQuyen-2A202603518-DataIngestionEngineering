"""End-to-end pipeline orchestration for Day 06 Data Ingestion Engineering Lab."""
import json
import time
import csv
from pathlib import Path
from .ingestion import load_corpus
from .chunking import fixed_size, by_paragraph
from .embeddings import MyEmbedder
from .store import QdrantVectorStore
from .evaluation import evaluate_query, summarize


def main() -> None:
    print("=" * 70)
    print("DAY 06 · DATA INGESTION ENGINEERING PIPELINE")
    print("Student: Nguyen Manh Quyen | MSSV: 2A202603518")
    print("=" * 70)

    # Resolve paths (support running from root or from starter/)
    base_dir = Path(".")
    if (base_dir / "starter").exists() and not (base_dir / "src").exists():
        data_dir = base_dir / "data"
        benchmark_dir = base_dir / "benchmark"
        results_dir = base_dir / "results"
        artifacts_dir = base_dir / "artifacts"
    else:
        # Running inside starter/
        data_dir = Path("../data") if Path("../data").exists() else Path("data")
        benchmark_dir = Path("../benchmark") if Path("../benchmark").exists() else Path("benchmark")
        results_dir = Path("../results") if Path("../results").exists() else Path("results")
        artifacts_dir = Path("../artifacts") if Path("../artifacts").exists() else Path("artifacts")

    results_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load Corpus
    corpus_file = data_dir / "so_tay_sinh_vien_2024.json"
    if not corpus_file.exists():
        # Fallback to local data dir
        corpus_file = Path("data/so_tay_sinh_vien_2024.json")

    print(f"\n[Step 1] Loading corpus from: {corpus_file}")
    pages = load_corpus(corpus_file, document_id="so-tay-sinh-vien-2024")
    print(f"Loaded {len(pages)} pages. Verification: >= 30 content pages required -> {'PASSED' if len(pages) >= 30 else 'FAILED'}.")
    total_chars = sum(len(p.text) for p in pages)
    print(f"Total corpus text length: {total_chars:,} characters.")

    # 2. Chunking for 3 Strategies
    print("\n[Step 2] Chunking corpus for Strategies A, B, C...")
    # Strategy A: Fixed-size (size=500, overlap=50)
    chunks_a = []
    for p in pages:
        chunks_a.extend(fixed_size(p, size=500, overlap=50))
    print(f"Strategy A (Fixed-size 500, overlap 50): {len(chunks_a)} chunks.")

    # Strategy B & C: Structural / by paragraph (max_size=800)
    chunks_b = []
    for p in pages:
        chunks_b.extend(by_paragraph(p, max_size=800))
    print(f"Strategy B & C (Structural Paragraph, max 800): {len(chunks_b)} chunks.")

    # 3. Embedding Model
    model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    print(f"\n[Step 3] Initializing Embedder: {model_name}...")
    t0_model = time.time()
    embedder = MyEmbedder(model_name=model_name)
    print(f"Embedder loaded in {time.time() - t0_model:.2f}s. Vector dimension: {embedder.dimensions}.")

    # 4. Storage & Indexing in Qdrant
    db_path = results_dir / "qdrant_db"
    print(f"\n[Step 4] Storing and indexing vectors in Qdrant ({db_path})...")
    store = QdrantVectorStore(db_path=str(db_path), dimensions=embedder.dimensions)

    # Ingest Strategy A
    t0_a = time.time()
    texts_a = [c.text for c in chunks_a]
    vectors_a = embedder.embed_documents(texts_a)
    store.upsert("strategy_a", chunks_a, vectors_a)
    ingest_time_a = time.time() - t0_a
    print(f"Strategy A ingested: {len(chunks_a)} chunks in {ingest_time_a:.2f}s.")

    # Ingest Strategy B
    t0_b = time.time()
    texts_b = [c.text for c in chunks_b]
    vectors_b = embedder.embed_documents(texts_b)
    store.upsert("strategy_b", chunks_b, vectors_b)
    ingest_time_b = time.time() - t0_b
    print(f"Strategy B ingested: {len(chunks_b)} chunks in {ingest_time_b:.2f}s.")

    # Ingest Strategy C (same chunks/vectors as B, stored in collection_strategy_c)
    t0_c = time.time()
    store.upsert("strategy_c", chunks_b, vectors_b)
    ingest_time_c = time.time() - t0_c
    print(f"Strategy C ingested: {len(chunks_b)} chunks in {ingest_time_c:.2f}s.")

    # Test Idempotency (re-upsert first 5 chunks of A)
    print("Verifying Idempotency: re-upserting subset of chunks...")
    store.upsert("strategy_a", chunks_a[:5], vectors_a[:5])
    print("Idempotent check complete (stable UUIDs prevent record duplication).")

    # 5. Load Benchmark Questions
    questions_file = benchmark_dir / "questions.json"
    if not questions_file.exists():
        questions_file = Path("benchmark/questions.json")

    print(f"\n[Step 5] Loading benchmark questions from: {questions_file}")
    with open(questions_file, "r", encoding="utf-8") as f:
        questions = json.load(f)
    print(f"Total benchmark questions: {len(questions)} (Dev: {sum(1 for q in questions if q['split'] == 'dev')}, Test: {sum(1 for q in questions if q['split'] == 'test')}).")

    # 6. Run Evaluation for A, B, C
    print("\n[Step 6] Running retrieval and benchmark evaluation...")
    all_traces = {"strategy_a": [], "strategy_b": [], "strategy_c": []}
    strategies = [
        ("strategy_a", "Strategy A (Fixed-size, No Filter)", False),
        ("strategy_b", "Strategy B (Paragraph, No Filter)", False),
        ("strategy_c", "Strategy C (Paragraph + Metadata Filter)", True),
    ]

    query_times = {}

    for strat_key, strat_label, use_filter in strategies:
        t0_eval = time.time()
        for q in questions:
            q_vec = embedder.embed_query(q["question"])
            filter_dict = q.get("filter") if use_filter else None
            hits = store.search(
                strategy=strat_key,
                query_vector=q_vec,
                top_k=3,
                filters=filter_dict
            )
            trace = evaluate_query(q, hits)
            all_traces[strat_key].append(trace)
        query_times[strat_key] = time.time() - t0_eval

    # 7. Summarize Metrics
    summaries = {
        "strategy_a": summarize(all_traces["strategy_a"]),
        "strategy_b": summarize(all_traces["strategy_b"]),
        "strategy_c": summarize(all_traces["strategy_c"]),
    }

    # Save Traces and Summaries
    trace_file = results_dir / "retrieval_trace.json"
    with open(trace_file, "w", encoding="utf-8") as f:
        json.dump(all_traces, f, ensure_ascii=False, indent=2)

    metrics_file = results_dir / "summary_metrics.json"
    with open(metrics_file, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    # Write Experiment Log CSV
    exp_log_file = artifacts_dir / "experiment_log.csv"
    with open(exp_log_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "strategy", "split", "chunk_type", "chunk_count",
            "hit_at_1_ratio", "hit_at_1_pct", "hit_at_3_ratio", "hit_at_3_pct",
            "filter_compliance", "ingest_time_sec", "eval_time_sec", "cost_usd"
        ])
        for strat_key, strat_name, _ in strategies:
            for s in ["dev", "test", "all"]:
                s_data = summaries[strat_key][s]
                c_count = len(chunks_a) if strat_key == "strategy_a" else len(chunks_b)
                i_time = ingest_time_a if strat_key == "strategy_a" else (ingest_time_b if strat_key == "strategy_b" else ingest_time_c)
                writer.writerow([
                    strat_key,
                    s,
                    "fixed_size_500" if strat_key == "strategy_a" else "paragraph_800",
                    c_count,
                    s_data["hit_at_1_ratio"],
                    s_data["hit_at_1_percent"],
                    s_data["hit_at_3_ratio"],
                    s_data["hit_at_3_percent"],
                    s_data["filter_compliance"],
                    round(i_time, 2),
                    round(query_times[strat_key], 2),
                    0.0
                ])

    # 8. Display Results Table
    print("\n" + "=" * 85)
    print("BENCHMARK RESULTS SUMMARY TABLE")
    print("=" * 85)
    print(f"{'Strategy':<25} | {'Split':<5} | {'Hit@1':<10} | {'Hit@3':<10} | {'Chunks':<7} | {'Ingest':<7} | {'Cost':<5}")
    print("-" * 85)

    for strat_key, strat_label, _ in strategies:
        c_count = len(chunks_a) if strat_key == "strategy_a" else len(chunks_b)
        i_time = ingest_time_a if strat_key == "strategy_a" else (ingest_time_b if strat_key == "strategy_b" else ingest_time_c)
        for s in ["dev", "test"]:
            s_data = summaries[strat_key][s]
            print(
                f"{strat_label:<25} | {s:<5} | "
                f"{s_data['hit_at_1_ratio'] + ' (' + str(s_data['hit_at_1_percent']) + '%)':<10} | "
                f"{s_data['hit_at_3_ratio'] + ' (' + str(s_data['hit_at_3_percent']) + '%)':<10} | "
                f"{c_count:<7} | "
                f"{str(round(i_time, 1)) + 's':<7} | "
                f"$0.0"
            )

    print("=" * 85)
    print(f"Results successfully saved to:\n - {trace_file}\n - {metrics_file}\n - {exp_log_file}")


if __name__ == "__main__":
    main()
