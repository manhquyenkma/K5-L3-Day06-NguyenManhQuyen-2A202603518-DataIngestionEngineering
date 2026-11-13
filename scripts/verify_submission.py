"""Verify all requirements and submission checklist items for Day 06 Lab."""
import json
import csv
from pathlib import Path


def main():
    print("=" * 60)
    print("SUBMISSION CHECKLIST VERIFICATION")
    print("=" * 60)
    passed_all = True

    # 1. Corpus verification
    corpus_path = Path("data/so_tay_sinh_vien_2024.json")
    manifest_path = Path("data/manifest.json")
    if not corpus_path.exists() or not manifest_path.exists():
        print("[FAIL] Corpus or manifest file missing!")
        passed_all = False
    else:
        with open(corpus_path, encoding="utf-8") as f:
            corpus = json.load(f)
        total_pages = len(corpus)
        min_chars = min(len(p["text"]) for p in corpus)
        total_chars = sum(len(p["text"]) for p in corpus)
        if total_pages >= 30 and min_chars >= 1500:
            print(f"[PASS] Corpus: {total_pages} pages (>=30), min {min_chars} chars (>=1500), total {total_chars:,} chars.")
        else:
            print(f"[FAIL] Corpus does not meet page/character constraints: {total_pages} pages, min {min_chars} chars.")
            passed_all = False

    # 2. Benchmark verification
    benchmark_path = Path("benchmark/questions.json")
    if not benchmark_path.exists():
        print("[FAIL] Benchmark questions file missing!")
        passed_all = False
    else:
        with open(benchmark_path, encoding="utf-8") as f:
            questions = json.load(f)
        dev_count = sum(1 for q in questions if q["split"] == "dev")
        test_count = sum(1 for q in questions if q["split"] == "test")
        filter_count = sum(1 for q in questions if q.get("filter") is not None)
        test_filter_count = sum(1 for q in questions if q["split"] == "test" and q.get("filter") is not None)
        
        # Verify evidence existence in corpus
        corpus_texts = {p["page"]: p["text"] for p in corpus}
        evidence_ok = True
        for q in questions:
            p_text = corpus_texts.get(q["gold_page"], "")
            if q["evidence_quote"] not in p_text:
                evidence_ok = False
                print(f"[FAIL] Evidence quote for question {q['id']} not in page {q['gold_page']}")
        
        if len(questions) >= 20 and dev_count >= 15 and test_count >= 5 and filter_count >= 3 and test_filter_count >= 1 and evidence_ok:
            print(f"[PASS] Benchmark: {len(questions)} questions ({dev_count} dev, {test_count} test), {filter_count} filter questions ({test_filter_count} in test). All quotes verified.")
        else:
            print(f"[FAIL] Benchmark does not meet criteria: {len(questions)} questions, dev={dev_count}, test={test_count}, filter={filter_count}")
            passed_all = False

    # 3. Traces and Results
    trace_path = Path("results/retrieval_trace.json")
    summary_path = Path("results/summary_metrics.json")
    audit_path = Path("results/human_audit.json")
    exp_log_path = Path("artifacts/experiment_log.csv")

    for p, name in [(trace_path, "Retrieval trace"), (summary_path, "Summary metrics"), (audit_path, "Human audit"), (exp_log_path, "Experiment log")]:
        if p.exists() and p.stat().st_size > 0:
            print(f"[PASS] {name}: exists ({p.stat().st_size:,} bytes).")
        else:
            print(f"[FAIL] {name} is missing or empty!")
            passed_all = False

    # 4. Student info and Report
    student_path = Path("STUDENT.md")
    report_custom = Path("report/individual/2A202603518_NguyenManhQuyen.md")
    report_template = Path("report/individual/MSSV_HoTen.md")

    if student_path.exists():
        content = student_path.read_text(encoding="utf-8")
        if "Nguyễn Mạnh Quyền" in content and "2A202603518" in content:
            print("[PASS] STUDENT.md: complete with student name and MSSV.")
        else:
            print("[FAIL] STUDENT.md is incomplete!")
            passed_all = False

    if report_custom.exists() and report_custom.stat().st_size > 1000:
        print(f"[PASS] Individual Report: {report_custom.name} exists ({report_custom.stat().st_size:,} bytes).")
    else:
        print("[FAIL] Individual Report missing or too short!")
        passed_all = False

    print("=" * 60)
    if passed_all:
        print("ALL SUBMISSION CRITERIA PASSED! Ready to submit.")
    else:
        print("SOME CHECKS FAILED! Please review issues above.")
    print("=" * 60)


if __name__ == "__main__":
    main()
