# Day 06 · Data Ingestion Engineering Lab

**Học viên:** Nguyễn Mạnh Quyền | **MSSV:** 2A202603518 | **Lớp:** K5-L3  
**Repository:** [K5-L3-Day06-NguyenManhQuyen-2A202603518-DataIngestionEngineering](https://github.com/manhquyenkma/K5-L3-Day06-NguyenManhQuyen-2A202603518-DataIngestionEngineering)

Bài thực hành cá nhân thiết kế và hiện thực Data Ingestion Pipeline hoàn chỉnh cho AI Retrieval, so sánh có kiểm soát **3 chiến lược dữ liệu** trên cùng một tập corpus và benchmark 20 câu hỏi theo đúng chuẩn 5 khía cạnh đánh giá của môn học.

---

## 1. Tổng quan Corpus và Dữ liệu

- **Chủ đề:** Sổ tay Sinh viên và Quy chế Đào tạo - Khảo thí - Công tác Sinh viên (Năm học 2024 - 2025).
- **Quy mô:** **32 trang nội dung độc lập**, tổng cộng **54.502 ký tự** (trang ngắn nhất đạt 1.502 ký tự, thỏa mãn tuyệt đối tiêu chí tối thiểu 1.500 ký tự/trang và >= 30 trang theo `GUIDE.md`).
- **Phân vùng (`section`):**
  - `dao_tao` (Trang 1–10): Chương trình học, tín chỉ, đăng ký, cảnh báo, tốt nghiệp.
  - `khao_thi` (Trang 11–16): Phòng thi, hoãn thi, phúc khảo, kỷ luật phòng thi.
  - `cong_tac_sinh_vien` (Trang 17–22): Đánh giá rèn luyện, khen thưởng, kỷ luật, thủ tục.
  - `hoc_bong_hoc_phi` (Trang 23–27): Học bổng KKHT, miễn giảm học phí, hạn nộp học phí.
  - `ky_tuc_xa` (Trang 28–32): Ưu tiên nội trú, nội quy giờ giấc, PCCC, vi phạm KTX.
- **Manifest:** [data/manifest.json](data/manifest.json).
- **File dữ liệu:** [data/so_tay_sinh_vien_2024.json](data/so_tay_sinh_vien_2024.json).

---

## 2. Ba chiến lược dữ liệu và Mô hình

| Tiêu chí | Chiến lược A | Chiến lược B | Chiến lược C |
|---|---|---|---|
| **Cơ chế Chunking** | Fixed-size window (500 ký tự, overlap 50 ký tự) | Structural Paragraph (Điều/Khoản, max 800 ký tự, ngắt theo câu) | Structural Paragraph (giống hệt B) |
| **Số lượng Chunks** | 132 chunks | 102 chunks | 102 chunks |
| **Embedding Model** | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (384 chiều, local) | Cùng model nhúng | Cùng model nhúng |
| **Vector Store** | Qdrant embedded persistent (`results/qdrant_db`) | Qdrant embedded persistent | Qdrant embedded persistent |
| **Truy xuất Top-3** | Cosine similarity, **không lọc** | Cosine similarity, **không lọc** | Cosine similarity, **lọc metadata (`section`)** |

- **So sánh A–B:** Phân tích ảnh hưởng của cơ chế chia chunk (Fixed-size vs Paragraph Structural).
- **So sánh B–C:** Cô lập 100% biến số chunk và embedding để đo lường riêng biệt tác động của **Metadata Filtering**.

---

## 3. Benchmark và Đánh giá 5 khía cạnh

- **Bộ câu hỏi:** 20 câu hỏi ([benchmark/questions.json](benchmark/questions.json)), phân chia trước: **15 Dev (`q01`–`q15`) / 5 Test (`q16`–`q20`)**.
- **Câu hỏi Filter:** 4 câu (`q04`, `q08`, `q12` ở Dev; `q18` ở Test).
- **Độ bao phủ câu hỏi:** Câu hỏi trực tiếp, câu hỏi diễn đạt lại, câu hỏi điều kiện/ngoại lệ, câu hỏi lọc metadata.

### Kết quả tóm tắt

| Chiến lược | Split | Hit@1 | Evidence Hit@3 | Coherence (TB/2) | Filter Compliance | Grounding (TB/2) |
|---|---|---|---|---|---|---|
| **Strategy A** | Dev | 9/15 (60.0%) | 10/15 (66.7%) | 0.20 / 2 | 1/3 (33.3%) | - |
| **Strategy A** | Test | 1/5 (20.0%) | 3/5 (60.0%) | 0.20 / 2 | 0/1 (0.0%) | 1.60 / 2 |
| **Strategy B** | Dev | 7/15 (46.7%) | 10/15 (66.7%) | 2.00 / 2 | 1/3 (33.3%) | - |
| **Strategy B** | Test | 2/5 (40.0%) | 3/5 (60.0%) | 2.00 / 2 | 0/1 (0.0%) | 1.60 / 2 |
| **Strategy C** | Dev | 7/15 (46.7%) | 10/15 (66.7%) | 2.00 / 2 | **3/3 (100.0%)** | - |
| **Strategy C** | Test | 2/5 (40.0%) | 3/5 (60.0%) | 2.00 / 2 | **1/1 (100.0%)** | 1.60 / 2 |

- **Báo cáo chi tiết cá nhân:** [report/individual/2A202603518_NguyenManhQuyen.md](report/individual/2A202603518_NguyenManhQuyen.md).
- **Trace chi tiết:** [results/retrieval_trace.json](results/retrieval_trace.json).
- **Nhật ký thí nghiệm:** [artifacts/experiment_log.csv](artifacts/experiment_log.csv).
- **Dữ liệu chấm thủ công (Audit):** [results/human_audit.json](results/human_audit.json).

---

## 4. Cài đặt và Tái lập kết quả

### Yêu cầu môi trường
- Python 3.11+
- Các thư viện cần thiết:
  ```bash
  pip install sentence-transformers qdrant-client
  ```

### Lệnh chạy Pipeline toàn diện
Chạy pipeline từ thư mục gốc repository:
```bash
python -m src.run
```
Hoặc chạy từ thư mục `starter/`:
```bash
cd starter
python -m src.run
```

Lệnh trên sẽ tự động:
1. Nạp và chuẩn hóa corpus 32 trang văn bản.
2. Cắt chunk theo Strategy A (132 chunks) và Strategy B/C (102 chunks).
3. Tạo vector nhúng 384 chiều bằng mô hình đa ngữ Sentence Transformers.
4. Nạp vào Qdrant persistent storage trên đĩa (`results/qdrant_db/`) và kiểm chứng tính Idempotent (không nhân đôi bản ghi).
5. Chạy truy xuất Top-3 cho cả 20 câu hỏi qua cả 3 chiến lược.
6. Tính toán các chỉ số Hit@1, Hit@3, Filter Compliance.
7. Xuất trace và bảng tóm tắt ra console và các file kết quả.
