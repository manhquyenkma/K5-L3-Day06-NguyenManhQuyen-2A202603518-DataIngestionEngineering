"""Verify and create benchmark questions.
Ensures every evidence_quote exists verbatim in the corresponding page text.
"""
import json
from pathlib import Path

# Load corpus
with open("data/so_tay_sinh_vien_2024.json", encoding="utf-8") as f:
    corpus = json.load(f)

corpus_by_page = {p["page"]: p["text"] for p in corpus}

questions = [
    # === DEV SET (15 QUESTIONS: q01 - q15) ===
    {
        "id": "q01",
        "split": "dev",
        "type": "truc_tiep",
        "question": "Một tín chỉ lý thuyết được quy định tương đương với bao nhiêu tiết học trên lớp?",
        "expected_answer": "15 tiết học lý thuyết trên lớp",
        "gold_source_id": "so-tay-sinh-vien-2024",
        "gold_page": 1,
        "evidence_quote": "Một tín chỉ (TC) được quy định tương đương với 15 tiết học lý thuyết trên lớp",
        "filter": None
    },
    {
        "id": "q02",
        "split": "dev",
        "type": "truc_tiep",
        "question": "Sinh viên có học lực bình thường được đăng ký tối đa bao nhiêu tín chỉ trong một học kỳ chính?",
        "expected_answer": "Tối đa 24 tín chỉ trong mỗi học kỳ chính",
        "gold_source_id": "so-tay-sinh-vien-2024",
        "gold_page": 2,
        "evidence_quote": "Sinh viên có học lực bình thường được đăng ký tối thiểu 14 tín chỉ và tối đa 24 tín chỉ trong mỗi học kỳ chính.",
        "filter": None
    },
    {
        "id": "q03",
        "split": "dev",
        "type": "dieu_kien_ngoai_le",
        "question": "Sinh viên xếp loại học lực yếu hoặc đang bị cảnh báo học tập chỉ được đăng ký tối đa bao nhiêu tín chỉ trong kỳ chính?",
        "expected_answer": "Tối đa không quá 14 tín chỉ trong một học kỳ chính",
        "gold_source_id": "so-tay-sinh-vien-2024",
        "gold_page": 2,
        "evidence_quote": "Sinh viên xếp loại học lực yếu hoặc đang trong tình trạng cảnh báo học tập chỉ được phép đăng ký tối thiểu 10 tín chỉ và tối đa không quá 14 tín chỉ trong một học kỳ chính",
        "filter": None
    },
    {
        "id": "q04",
        "split": "dev",
        "type": "metadata_filter",
        "question": "Thời hạn nộp đơn rút bớt học phần trong học kỳ chính là bao lâu kể từ ngày bắt đầu học tập?",
        "expected_answer": "Trong vòng 2 tuần đầu tiên của học kỳ chính",
        "gold_source_id": "so-tay-sinh-vien-2024",
        "gold_page": 3,
        "evidence_quote": "Thời hạn nộp đơn rút bớt học phần: Trong vòng 2 tuần đầu tiên của học kỳ chính và trong vòng 1 tuần đầu tiên của học kỳ hè",
        "filter": {"section": "dao_tao"}
    },
    {
        "id": "q05",
        "split": "dev",
        "type": "dien_dat_lai",
        "question": "Những học phần nào thì sinh viên được phép đăng ký học để cải thiện nâng cao điểm tích lũy?",
        "expected_answer": "Các học phần đã đạt điểm D hoặc D+",
        "gold_source_id": "so-tay-sinh-vien-2024",
        "gold_page": 3,
        "evidence_quote": "Sinh viên được phép đăng ký học cải thiện điểm đối với các học phần đã đạt điểm D hoặc D+ nhằm nâng cao điểm trung bình tích lũy.",
        "filter": None
    },
    {
        "id": "q06",
        "split": "dev",
        "type": "dieu_kien_ngoai_le",
        "question": "Sinh viên năm thứ ba bị cảnh báo kết quả học tập khi điểm trung bình tích lũy giảm xuống dưới mức nào?",
        "expected_answer": "Dưới 1.60 đối với sinh viên năm thứ ba",
        "gold_source_id": "so-tay-sinh-vien-2024",
        "gold_page": 4,
        "evidence_quote": "dưới 1.60 đối với sinh viên năm thứ ba; dưới 1.80 đối với sinh viên các năm tiếp theo",
        "filter": None
    },
    {
        "id": "q07",
        "split": "dev",
        "type": "truc_tiep",
        "question": "Thời gian nghỉ học tạm thời vì nhu cầu cá nhân tối đa không được vượt quá bao nhiêu học kỳ chính?",
        "expected_answer": "Không được vượt quá 4 học kỳ chính (tương đương 2 năm học) trong toàn khóa học",
        "gold_source_id": "so-tay-sinh-vien-2024",
        "gold_page": 5,
        "evidence_quote": "Thời gian nghỉ học tạm thời vì nhu cầu cá nhân được tính theo từng học kỳ và không được vượt quá 4 học kỳ chính (tương đương 2 năm học) trong toàn khóa học.",
        "filter": None
    },
    {
        "id": "q08",
        "split": "dev",
        "type": "metadata_filter",
        "question": "Sinh viên đăng ký học cùng lúc hai chương trình (song bằng) cần đạt điểm trung bình tích lũy chương trình 1 tối thiểu là bao nhiêu?",
        "expected_answer": "Đạt từ 2.50 trở lên tại thời điểm đăng ký",
        "gold_source_id": "so-tay-sinh-vien-2024",
        "gold_page": 6,
        "evidence_quote": "Điểm trung bình chung tích lũy của chương trình thứ nhất đạt từ 2.50 trở lên tại thời điểm đăng ký, đồng thời không bị cảnh báo học tập trong cả hai học kỳ gần nhất",
        "filter": {"section": "dao_tao"}
    },
    {
        "id": "q09",
        "split": "dev",
        "type": "dieu_kien_ngoai_le",
        "question": "Điểm trung bình tích lũy tối thiểu và tỷ lệ tín chỉ tích lũy cần thiết để sinh viên được nhận làm đồ án tốt nghiệp là gì?",
        "expected_answer": "Tích lũy tối thiểu 85% tổng số tín chỉ và điểm trung bình tích lũy đạt từ 2.60 trở lên",
        "gold_source_id": "so-tay-sinh-vien-2024",
        "gold_page": 8,
        "evidence_quote": "Tích lũy tối thiểu 85% tổng số tín chỉ của chương trình đào tạo ngành học;\nb) Điểm trung bình chung tích lũy tính đến thời điểm xét đạt từ 2.60 trở lên",
        "filter": None
    },
    {
        "id": "q10",
        "split": "dev",
        "type": "dien_dat_lai",
        "question": "Thí sinh đến muộn bao nhiêu phút sau khi phát đề thi thì sẽ không được vào thi và bị điểm 0?",
        "expected_answer": "Đến muộn quá 15 phút sau khi phát đề thi",
        "gold_source_id": "so-tay-sinh-vien-2024",
        "gold_page": 11,
        "evidence_quote": "Thí sinh đến muộn quá 15 phút sau khi phát đề thi (đối với bài thi tự luận) hoặc sau khi bắt đầu ca thi (đối với bài thi trắc nghiệm trên máy tính) sẽ không được phép dự thi và bị tính điểm 0 (không) cho buổi thi đó.",
        "filter": None
    },
    {
        "id": "q11",
        "split": "dev",
        "type": "dieu_kien_ngoai_le",
        "question": "Trong trường hợp nào thì đơn xin hoãn thi của sinh viên sẽ không được xem xét và bị tính điểm 0?",
        "expected_answer": "Đơn nộp quá thời hạn 3 ngày làm việc kể từ ngày tổ chức ca thi",
        "gold_source_id": "so-tay-sinh-vien-2024",
        "gold_page": 12,
        "evidence_quote": "Đơn nộp quá thời hạn 3 ngày nêu trên sẽ không được xem xét, sinh viên bị tính điểm 0 cho bài thi vắng mặt không lý do.",
        "filter": None
    },
    {
        "id": "q12",
        "split": "dev",
        "type": "metadata_filter",
        "question": "Thời hạn nộp đơn đề nghị phúc khảo bài thi kết thúc học phần là bao nhiêu ngày kể từ khi công bố điểm thi?",
        "expected_answer": "Trong vòng 7 ngày làm việc kể từ ngày công bố điểm thi chính thức",
        "gold_source_id": "so-tay-sinh-vien-2024",
        "gold_page": 14,
        "evidence_quote": "Thời hạn nộp đơn phúc khảo: Trong vòng 7 ngày làm việc kể từ ngày Phòng Khảo thí công bố điểm thi chính thức trên cổng portal sinh viên.",
        "filter": {"section": "khao_thi"}
    },
    {
        "id": "q13",
        "split": "dev",
        "type": "truc_tiep",
        "question": "Thí sinh bị kỷ luật khiển trách trong kỳ thi sẽ bị trừ bao nhiêu phần trăm số điểm bài thi môn đó?",
        "expected_answer": "Bị trừ 25% tổng số điểm của bài thi môn đó",
        "gold_source_id": "so-tay-sinh-vien-2024",
        "gold_page": 15,
        "evidence_quote": "Thí sinh bị kỷ luật khiển trách trong kỳ thi môn nào sẽ bị trừ 25% tổng số điểm của bài thi môn đó.",
        "filter": None
    },
    {
        "id": "q14",
        "split": "dev",
        "type": "truc_tiep",
        "question": "Điểm rèn luyện của sinh viên được đánh giá theo thang điểm bao nhiêu và chia thành mấy tiêu chí?",
        "expected_answer": "Thang điểm 100, phân bổ vào 5 tiêu chí thành phần",
        "gold_source_id": "so-tay-sinh-vien-2024",
        "gold_page": 17,
        "evidence_quote": "Điểm rèn luyện được đánh giá theo thang điểm 100, phân bổ vào 5 tiêu chí thành phần cụ thể như sau",
        "filter": None
    },
    {
        "id": "q15",
        "split": "dev",
        "type": "dieu_kien_ngoai_le",
        "question": "Sinh viên bị xếp loại rèn luyện Yếu hoặc Kém trong mấy học kỳ liên tiếp thì sẽ bị tạm ngừng học tập?",
        "expected_answer": "Trong 02 học kỳ liên tiếp sẽ phải tạm ngừng học tập 01 học kỳ chính tiếp theo",
        "gold_source_id": "so-tay-sinh-vien-2024",
        "gold_page": 18,
        "evidence_quote": "Sinh viên bị xếp loại rèn luyện Yếu hoặc Kém trong 02 học kỳ liên tiếp sẽ phải tạm ngừng học tập 01 học kỳ chính tiếp theo",
        "filter": None
    },

    # === TEST SET (5 QUESTIONS: q16 - q20) ===
    {
        "id": "q16",
        "split": "test",
        "type": "truc_tiep",
        "question": "Để đạt học bổng khuyến khích học tập mức Xuất sắc, sinh viên cần đạt điểm học tập và điểm rèn luyện như thế nào?",
        "expected_answer": "Điểm trung bình học tập từ 3.60 đến 4.00 và điểm rèn luyện đạt từ 90 điểm trở lên (loại Xuất sắc)",
        "gold_source_id": "so-tay-sinh-vien-2024",
        "gold_page": 23,
        "evidence_quote": "Mức Xuất sắc: Cấp cho sinh viên có Điểm trung bình học tập (ĐTBHT) đạt từ 3.60 đến 4.00 và ĐRL đạt loại Xuất sắc (từ 90 điểm trở lên). Mức học bổng bằng 120% mức trần học phí của ngành học",
        "filter": None
    },
    {
        "id": "q17",
        "split": "test",
        "type": "dieu_kien_ngoai_le",
        "question": "Sinh viên là con của cán bộ công chức bị tai nạn lao động hoặc bệnh nghề nghiệp được giảm bao nhiêu phần trăm học phí?",
        "expected_answer": "Được giảm 50% học phí",
        "gold_source_id": "so-tay-sinh-vien-2024",
        "gold_page": 25,
        "evidence_quote": "Đối tượng được giảm 50% học phí:\nSinh viên là con của cán bộ, công chức, viên chức, công nhân mà cha hoặc mẹ bị tai nạn lao động hoặc mắc bệnh nghề nghiệp được hưởng trợ cấp thường xuyên",
        "filter": None
    },
    {
        "id": "q18",
        "split": "test",
        "type": "metadata_filter",
        "question": "Thời hạn hoàn thành toàn bộ học phí của học kỳ chính là trong vòng mấy tuần đầu tiên của kỳ học?",
        "expected_answer": "Trong vòng 6 tuần đầu tiên của học kỳ (tương ứng 42 ngày)",
        "gold_source_id": "so-tay-sinh-vien-2024",
        "gold_page": 27,
        "evidence_quote": "Thời hạn nộp học phí: Sinh viên phải hoàn thành toàn bộ học phí của học kỳ chính trong vòng 6 tuần đầu tiên của học kỳ (tương ứng 42 ngày kể từ ngày bắt đầu học tập).",
        "filter": {"section": "hoc_bong_hoc_phi"}
    },
    {
        "id": "q19",
        "split": "test",
        "type": "dien_dat_lai",
        "question": "Sinh viên nội trú ký túc xá phải có mặt tại phòng ở trước mấy giờ đêm theo quy định giờ giới nghiêm?",
        "expected_answer": "Trước 23h00 hàng ngày",
        "gold_source_id": "so-tay-sinh-vien-2024",
        "gold_page": 30,
        "evidence_quote": "Giờ đóng cửa KTX (giờ giới nghiêm): 23h00 hàng ngày. Tất cả sinh viên nội trú phải có mặt tại phòng ở trước 23h00.",
        "filter": None
    },
    {
        "id": "q20",
        "split": "test",
        "type": "dieu_kien_ngoai_le",
        "question": "Hành vi nấu ăn trong phòng ở Ký túc xá bằng bếp gas hoặc bếp từ sẽ bị xử lý kỷ luật ở mức nào?",
        "expected_answer": "Bị kỷ luật cảnh cáo cấp Ký túc xá cho lần đầu vi phạm",
        "gold_source_id": "so-tay-sinh-vien-2024",
        "gold_page": 32,
        "evidence_quote": "Cảnh cáo cấp Ký túc xá: Áp dụng đối với các vi phạm: Đã bị khiển trách mà tái phạm; nấu ăn trong phòng ở lần đầu; tự ý câu móc điện, nước",
        "filter": None
    }
]

# Verification of evidence existence
errors = []
for q in questions:
    p_num = q["gold_page"]
    page_text = corpus_by_page.get(p_num, "")
    quote = q["evidence_quote"]
    if quote not in page_text:
        errors.append((q["id"], p_num, quote))

if errors:
    print(f"FAILED: {len(errors)} quotes not found in corpus text:")
    for eid, ep, eq in errors:
        print(f" - Question {eid} (page {ep}): '{eq[:50]}...'")
    raise ValueError("Evidence verification failed!")
else:
    print(f"VERIFIED: All {len(questions)} evidence quotes exist verbatim in corpus text.")

# Save to benchmark directory
bench_dir = Path("benchmark")
bench_dir.mkdir(exist_ok=True, parents=True)

with open(bench_dir / "questions.json", "w", encoding="utf-8") as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)

print(f"Saved benchmark to benchmark/questions.json")
dev_count = sum(1 for q in questions if q["split"] == "dev")
test_count = sum(1 for q in questions if q["split"] == "test")
filter_count = sum(1 for q in questions if q["filter"] is not None)
test_filter_count = sum(1 for q in questions if q["split"] == "test" and q["filter"] is not None)
print(f"Total: {len(questions)} (Dev: {dev_count}, Test: {test_count})")
print(f"Filter questions: {filter_count} total, {test_filter_count} in Test set.")

