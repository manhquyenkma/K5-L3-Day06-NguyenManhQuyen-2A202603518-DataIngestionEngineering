# Báo cáo cá nhân — Day 6 · Data Ingestion Engineering

- **Họ và tên:** Nguyễn Mạnh Quyền
- **MSSV:** 2A202603518
- **Lớp:** K5-L3
- **Repository:** [GitHub Repository](https://github.com/manhquyenkma/K5-L3-Day06-NguyenManhQuyen-2A202603518-DataIngestionEngineering)

---

## Dữ liệu và pipeline

- **Chủ đề, nguồn/quyền, số trang và quy tắc tính trang:**
  - *Chủ đề:* Sổ tay Sinh viên và Quy chế Đào tạo - Khảo thí - Công tác Sinh viên (Năm học 2024 - 2025).
  - *Nguồn và quyền:* Tài liệu quy chế công khai của trường đại học, cấp phép theo chuẩn Public University Academic Regulations / Creative Commons CC BY-SA 4.0. Không chứa dữ liệu cá nhân nhạy cảm, bí mật nội bộ hay thông tin cần bảo mật.
  - *Số trang và quy tắc tính trang:* Tổng cộng **32 đơn vị trang/chương học vụ độc lập** (vượt yêu cầu tối thiểu 30 trang của đề bài). Theo hướng dẫn GUIDE.md đối với dữ liệu văn bản/JSON phân đoạn, mỗi đơn vị tương đương một trang nội dung có **tối thiểu 1.500 ký tự chuẩn hóa** (trang ngắn nhất đạt 1.502 ký tự, trang dài nhất 1.978 ký tự, trung bình 1.703,2 ký tự/trang, tổng dung lượng toàn bộ corpus là 54.502 ký tự). Toàn bộ 32 trang đều là nội dung quy chế thực chất, không tính trang bìa, mục lục hay trang rỗng.
  - *Manifest:* Lưu trữ chi tiết tại `data/manifest.json`.

- **Chuẩn hóa, lỗi và giới hạn:**
  - *Chuẩn hóa Unicode:* Sử dụng `unicodedata.normalize("NFC", text)` để đồng nhất bảng mã tiếng Việt dựng sẵn; chuẩn hóa xuống dòng (`\r\n` -> `\n`), thay thế khoảng trắng không ngắt (`\u00a0`), tab và khoảng trắng liên tiếp bằng dấu cách đơn; duy trì ngắt đoạn (`\n\n`) để bảo toàn cấu trúc điều khoản pháp lý.
  - *Xử lý lỗi:* Module `ingestion.py` chủ động kiểm tra và ghi log cảnh báo đối với bất kỳ trang rỗng hoặc thiếu nội dung; xác thực kiểu dữ liệu và gán ID tài liệu nhất quán `so-tay-sinh-vien-2024`.
  - *Giới hạn dữ liệu:* Văn bản quy chế dạng văn bản chuẩn, chưa bao gồm bảng biểu ma trận phức tạp hoặc lưu đồ quy trình dạng hình ảnh cần xử lý Vision/OCR.

- **Embedding model/provider/version/số chiều, vector store/version, metric, lệnh chạy và chi phí:**
  - *Embedding model:* `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (Sentence Transformers v6.3.0). Chạy hoàn toàn **local trên CPU/RAM**, số chiều vector là **384**, chuẩn hóa L2 norm.
  - *Vector store:* **Qdrant** embedded persistent storage (thư viện `qdrant-client` v1.20.0), lưu trữ bền vững trên đĩa tại thư mục `results/qdrant_db/` (hỗ trợ kiểm tra sau khi tắt tiến trình).
  - *Metric tìm kiếm:* Cosine Similarity (Qdrant `Distance.COSINE`).
  - *Lệnh chạy pipeline:* `python -m src.run` (hoặc chạy từ starter: `python -m src.run`).
  - *Chi phí:* **0.00 USD** (100% tài nguyên mã nguồn mở chạy local offline, không phụ thuộc API trả phí, không rủi ro cạn quota).

- **Metadata bắt buộc, trường lọc bổ sung, nguồn giá trị và lý do chọn:**
  - *Metadata bắt buộc:* `document_id` (`so-tay-sinh-vien-2024`), `source` (`data/so_tay_sinh_vien_2024.json`), `page` (số thứ tự trang/đơn vị từ 1 đến 32).
  - *Trường lọc bổ sung:*
    - `section`: Phân vùng nghiệp vụ quy chế, nhận một trong 5 giá trị chính thức:
      1. `dao_tao` (Trang 1–10: Chương trình học, tín chỉ, đăng ký, cảnh báo, tốt nghiệp).
      2. `khao_thi` (Trang 11–16: Phòng thi, hoãn thi, phúc khảo, kỷ luật thi cử).
      3. `cong_tac_sinh_vien` (Trang 17–22: Điểm rèn luyện, khen thưởng, kỷ luật, thủ tục).
      4. `hoc_bong_hoc_phi` (Trang 23–27: Học bổng KKHT, miễn giảm học phí, hạn nộp học phí).
      5. `ky_tuc_xa` (Trang 28–32: Thứ tự ưu tiên, nội quy giờ giấc, PCCC, vi phạm KTX).
    - `year`: Giá trị số nguyên `2024` (năm học ban hành quy chế).
    - `title`: Tên chương/tiêu đề phân đoạn.
  - *Lý do chọn:* Trường `section` phản ánh chính xác ranh giới thẩm quyền và nghiệp vụ trong trường đại học. Khi người dùng hỏi về học bổng hoặc học phí, việc lọc theo `hoc_bong_hoc_phi` ngăn chặn tuyệt đối tình trạng vector search bị phân tán sang các điều khoản về tín chỉ đào tạo hay khen thưởng rèn luyện.

---

## Cấu hình và benchmark

- **A / B / C (tham số cụ thể, khác biệt duy nhất B–C):**
  - **Chiến lược A (Fixed-size Window):** Cắt theo kích thước cố định bằng ký tự: `chunk_size = 500`, `chunk_overlap = 50`. Cắt cơ học trượt qua văn bản, gắn đầy đủ metadata nguồn và trang, truy xuất Top-3 Cosine **không lọc metadata**.
  - **Chiến lược B (Structural / Paragraph Chunking):** Phân đoạn theo cấu trúc văn bản tự nhiên (dựa trên Điều, Khoản, đoạn `\n\n`), giới hạn `max_size = 800` ký tự. Nếu đoạn vượt quá 800 ký tự, thuật toán tách nhỏ theo ranh giới câu (`.` hoặc `;`) để bảo đảm trọn vẹn mệnh đề và chủ ngữ. Gắn cùng metadata, truy xuất Top-3 Cosine **không lọc metadata**.
  - **Chiến lược C (Structural Chunking + Metadata Filter):** Giữ **chính xác 100% tập chunk và vector nhúng của Chiến lược B**. Điểm khác biệt duy nhất nằm ở tầng truy xuất: Áp dụng **bộ lọc metadata** (`section`) khi câu hỏi có chỉ định filter; các câu không có filter sẽ truy xuất nguyên bản như B. Thiết kế này cô lập hoàn toàn biến số chunking để đo lường chính xác tác động của việc lọc metadata.

- **≥20 câu: phân chia ≥15 dev / ≥5 test, câu metadata filter và cách kiểm chứng evidence:**
  - Bộ câu hỏi gồm đúng **20 câu** được biên soạn và kiểm chứng trước khi chạy thí nghiệm: **15 câu Dev (`q01`–`q15`)** và **5 câu Test (`q16`–`q20`)**.
  - Cơ cấu độ đa dạng: Bao gồm câu hỏi trực tiếp (`truc_tiep`), câu hỏi diễn đạt lại (`dien_dat_lai`), câu hỏi chứa điều kiện/ngoại lệ (`dieu_kien_ngoai_le`), và **4 câu kiểm tra metadata filter** (`q04`, `q08`, `q12` trong Dev; `q18` trong Test, đáp ứng vượt tiêu chuẩn >= 3 câu filter và >= 1 câu test).
  - *Kiểm chứng evidence:* Toàn bộ 20/20 đoạn trích `evidence_quote` đều được script `create_benchmark.py` đối soát tự động, cam kết tồn tại nguyên văn 100% trong văn bản nguồn của đúng `gold_page`.

- **Tiêu chí chọn chiến lược đã chốt trước khi xem test:**
  1. *Tiêu chí 1 (Ưu tiên cao nhất):* Độ mạch lạc của chunk (Chunk Coherence) phải đạt mức hiểu trọn vẹn, không cắt đứt điều khoản pháp lý hoặc mất điều kiện điểm số/thời hạn.
  2. *Tiêu chí 2:* Evidence Hit@3 trên tập Dev ổn định, đảm bảo bằng chứng cần thiết nằm trong Top-3 để LLM có thể trả lời.
  3. *Tiêu chí 3:* Tỷ lệ tuân thủ lọc metadata (Filter Compliance) đạt 100% khi người dùng hoặc hệ thống cung cấp phạm vi nghiệp vụ.
  4. *Tiêu chí 4:* Tiết kiệm chi phí lưu trữ (số lượng chunk vừa phải, thời gian xử lý nhanh).

---

## Kết quả

### Bảng 1: Kết quả định lượng Retrieval, Dung lượng và Tài nguyên

| Strategy | Split | Hit@1 (n/N) | Evidence Hit@3 (n/N) | Chunk count | Thời gian ingest | Chi phí |
|---|---|---|---|---|---|---|
| **Strategy A** (Fixed 500, no filter) | dev | 9/15 (60.00%) | 10/15 (66.67%) | 132 | 11.32s | $0.00 |
| **Strategy A** (Fixed 500, no filter) | test | 1/5 (20.00%) | 3/5 (60.00%) | 132 | 11.32s | $0.00 |
| **Strategy B** (Paragraph 800, no filter) | dev | 7/15 (46.67%) | 10/15 (66.67%) | 102 | 9.21s | $0.00 |
| **Strategy B** (Paragraph 800, no filter) | test | 2/5 (40.00%) | 3/5 (60.00%) | 102 | 9.21s | $0.00 |
| **Strategy C** (Paragraph 800 + Filter) | dev | 7/15 (46.67%) | 10/15 (66.67%) | 102 | 0.52s (tái dùng) | $0.00 |
| **Strategy C** (Paragraph 800 + Filter) | test | 2/5 (40.00%) | 3/5 (60.00%) | 102 | 0.52s (tái dùng) | $0.00 |

*Ghi chú toàn cục (All 20 câu):*
- Strategy A: Hit@1 = 10/20 (50.00%), Hit@3 = 13/20 (65.00%).
- Strategy B: Hit@1 = 9/20 (45.00%), Hit@3 = 13/20 (65.00%).
- Strategy C: Hit@1 = 9/20 (45.00%), Hit@3 = 13/20 (65.00%).

---

### Bảng 2: Kết quả đánh giá chất lượng (Coherence, Metadata, Grounding)

| Strategy | Coherence trung bình /2 (n=10) | Metadata đủ và đúng (n/N) | Filter tuân thủ (n/N hoặc N/A) | Grounding 0/1/2 (số câu) và trung bình /2 |
|---|---|---|---|---|
| **Strategy A** | **0.20 / 2** (10 mẫu) | 15/15 (100.0%) | 0/1 (0.0% trên test) / 1/4 (25.0% all) | 0: 0 câu, 1: 2 câu, 2: 3 câu (TB: **1.60 / 2**) |
| **Strategy B** | **2.00 / 2** (10 mẫu) | 15/15 (100.0%) | 0/1 (0.0% trên test) / 1/4 (25.0% all) | 0: 0 câu, 1: 2 câu, 2: 3 câu (TB: **1.60 / 2**) |
| **Strategy C** | **2.00 / 2** (10 mẫu) | 15/15 (100.0%) | **1/1 (100.0% trên test) / 4/4 (100.0% all)** | 0: 0 câu, 1: 2 câu, 2: 3 câu (TB: **1.60 / 2**) |

- **Đường dẫn trace, nhãn thủ công và cách chọn mẫu:**
  - *Trace truy xuất chi tiết:* `results/retrieval_trace.json`.
  - *Bảng tổng hợp chỉ số:* `results/summary_metrics.json`.
  - *Nhật ký thí nghiệm CSV:* `artifacts/experiment_log.csv`.
  - *Bảng nhãn thủ công chi tiết:* `results/human_audit.json`.
  - *Quy tắc chọn mẫu Coherence:* Lấy 10 vị trí nguồn đầu tiên (Trang 1 đến Trang 10, tương ứng toàn bộ Phần Đào tạo), đánh giá chunk đầu tiên chứa vị trí đó trên thang điểm 0–2 theo tiêu chuẩn GUIDE.md trước khi phân tích kết quả retrieval.

---

## Phân tích và kết luận

### 1. So sánh chi tiết A–B và B–C

- **So sánh A–B (Tác động của Chiến lược Chia Chunk):**
  - *Số lượng chunk và hiệu năng:* Strategy A sinh ra 132 chunks (do cắt cố định 500 ký tự với overlap 50), trong khi Strategy B chỉ sinh ra 102 chunks (giảm 22.7% số lượng vector cần lưu trữ và tính toán), thời gian ingest giảm từ 11.32s xuống 9.21s.
  - *Tính mạch lạc (Coherence):* Đây là điểm khác biệt chấn động nhất. Strategy A đạt điểm cực thấp (**0.20/2**) vì thuật ngữ và mệnh đề pháp lý bị cắt đứt cơ học. Cụ thể:
    - Trang 2 bị cắt giữa từ `bậc...`, làm mất điều kiện đào tạo kỹ sư.
    - Trang 3 bị cắt cụt ngay tại `Điều kiện rút: Số tín chỉ còn...`, mất hoàn toàn số lượng 14 tín chỉ tối thiểu.
    - Trang 4 bị cắt đứt giữa từ viết tắt `ĐTB...`.
    - Trang 8 bị cắt trước số điểm `2.60`, làm mất điều kiện GPA làm đồ án tốt nghiệp.
    - Ngược lại, Strategy B bảo toàn nguyên vẹn 100% cấu trúc Điều/Khoản, đạt điểm tuyệt đối **2.00/2**.
  - *Độ chính xác truy xuất (Retrieval Accuracy):* Trên tập Dev, Strategy A có Hit@1 cao hơn một chút (60.0% vs 46.7%) do chunk nhỏ 500 ký tự có mật độ từ khóa cô đặc hơn với các câu hỏi ngắn; tuy nhiên Evidence Hit@3 của cả A và B đều đạt ngang nhau (66.67% trên Dev, 60.0% trên Test, 65.0% tổng thể). Trên tập Test, Strategy B vượt trội ở Hit@1 (40.0% vs 20.0%) nhờ giữ được nguyên khối ngữ cảnh của câu điều kiện phức tạp.

- **So sánh B–C (Tác động của Lọc Metadata Filter):**
  - Giữ nguyên cấu trúc chunk và embedding vector, Strategy C bổ sung bộ lọc metadata khi truy vấn có chỉ định phạm vi (`section`).
  - *Tỷ lệ tuân thủ filter (Filter Compliance):* Ở Strategy B, khi câu hỏi tìm kiếm về thời hạn học phí (`q18`), các kết quả Top-3 bị xâm lấn bởi các trang về quy định tín chỉ ở phần đào tạo (Trang 2, Trang 9) do có các từ khóa trùng lặp ("học kỳ chính", "thời hạn", "quy định"). Filter compliance của Strategy B chỉ đạt 0/1 trên Test và 1/4 trên toàn bộ câu filter.
  - Ở Strategy C, việc áp dụng `section = "hoc_bong_hoc_phi"` đã khóa chặt phạm vi, giúp 100% kết quả Top-3 nằm chính xác ở Trang 27, loại bỏ triệt để 100% nhiễu xuyên phân vùng (Filter compliance đạt **1/1** trên test và **4/4** trên toàn bộ benchmark).

---

### 2. Hai ví dụ sai có ID câu và nguồn phân tích

- **Ví dụ sai thứ nhất — Câu `q17` ở Strategy A:**
  - *ID câu:* `q17` (Split: Test).
  - *Câu hỏi:* "Sinh viên là con của cán bộ công chức bị tai nạn lao động hoặc bệnh nghề nghiệp được giảm bao nhiêu phần trăm học phí?"
  - *Gold evidence:* Nằm ở Trang 25 (`gold_page: 25`), nội dung Điều 50 Khoản 2: *"Đối tượng được giảm 50% học phí: Sinh viên là con của cán bộ, công chức, viên chức, công nhân mà cha hoặc mẹ bị tai nạn lao động hoặc mắc bệnh nghề nghiệp..."*
  - *Lỗi ở Strategy A:* Do cơ chế cắt cửa sổ 500 ký tự, Điều 50 bị bẻ đôi thành 2 chunk. Chunk rơi vào Rank 1 (`A_so-tay-sinh-vien-2024_p25_c2`) chỉ lấy được phần đuôi văn bản nhưng bị mất tiêu đề *"Đối tượng được giảm 50% học phí"*. Do đó, chunk truy xuất được thiếu mất con số "50%" cần thiết để trả lời câu hỏi! Kết quả: Hit@1 = False, Hit@3 = False.
  - *Đối chứng Strategy B:* Nhờ chunking theo đoạn, toàn bộ Điều 50 Khoản 2 nằm trọn vẹn trong một chunk `B_so-tay-sinh-vien-2024_p25_c1`, giúp Strategy B đạt Hit@1 = True với điểm tương đồng cao.

- **Ví dụ sai thứ hai — Câu `q16` ở Strategy B và C:**
  - *ID câu:* `q16` (Split: Test).
  - *Câu hỏi:* "Để đạt học bổng khuyến khích học tập mức Xuất sắc, sinh viên cần đạt điểm học tập và điểm rèn luyện như thế nào?"
  - *Gold evidence:* Nằm ở Trang 23 (`gold_page: 23`), nội dung Điều 46 Khoản 1a: *"Mức Xuất sắc: Cấp cho sinh viên có Điểm trung bình học tập đạt từ 3.60 đến 4.00 và ĐRL đạt loại Xuất sắc (từ 90 điểm trở lên)..."*
  - *Lỗi ở Strategy B và C:* Trang 23 có 2 điều khoản: Điều 45 (Nguyên tắc chung và điều kiện cần 15 TC) và Điều 46 (Các mức học bổng cụ thể). Do mô hình embedding đa ngữ nhận diện câu hỏi chung về "học bổng khuyến khích học tập", chunk chứa Điều 45 được xếp ở Rank 3, trong khi chunk chứa Điều 46 bị tụt xuống vị trí Rank 4 (score = 0.692). Kết quả Top-3 chỉ mang về Điều 45 (có điều kiện cần nhưng thiếu con số 3.60 và 90 điểm). Kết quả: Hit@1 = False, Hit@3 = False.
  - *Nguyên nhân cốt lõi:* Độ dài chunk của Strategy B lớn hơn (~700 ký tự) làm phân tán trọng số chú ý của vector so với các chunk siêu ngắn 500 ký tự ở Strategy A (vốn xếp Điều 46 ở Rank 3).

---

### 3. Chiến lược lựa chọn, đánh đổi và điều kiện áp dụng

- **Chiến lược được lựa chọn:** **Chiến lược C (Paragraph Structural Chunking + Metadata Filtering)**.
- **Lý do lựa chọn:**
  - Đạt điểm mạch lạc tuyệt đối **2.00 / 2**, loại bỏ nguy cơ AI trả lời sai do bị cắt vụn câu chữ như Chiến lược A.
  - Giảm 22.7% số lượng vector cần tính toán và lưu trữ so với Fixed-size, tiết kiệm RAM và thời gian embedding.
  - Khi có metadata filter, Chiến lược C loại bỏ 100% nhiễu xuyên phân vùng, bảo đảm tính an toàn và thẩm quyền của tài liệu tra cứu.
- **Đánh đổi (Trade-offs):**
  - Chunk cấu trúc đoạn có kích thước lớn hơn (~700 ký tự so với 500 ký tự), dẫn đến việc biểu diễn vector bị "loãng" đối với các câu hỏi nhắm vào chi tiết siêu nhỏ (như ví dụ `q16`), khiến thứ hạng của đoạn chứa đáp án có thể bị đẩy xuống sau các đoạn tổng quan.
  - Cần chi phí trích xuất metadata chuẩn hóa ở khâu tiền xử lý (cần nhận diện đúng `section`, `year`).
- **Điều kiện áp dụng:**
  - Phù hợp nhất cho các hệ thống hỏi đáp quy chế, tài liệu kỹ thuật, chính sách nhân sự hoặc sổ tay vận hành có cấu trúc chương/mục rõ ràng và người dùng có thể chọn trước danh mục tra cứu.

---

### 4. Hạn chế của nghiên cứu

1. *Quy mô tập Test:* Tập Test gồm 5 câu là đại diện thu nhỏ phục vụ đánh giá nhanh trong phòng lab, chưa đủ lớn để đưa ra kết luận thống kê p-value có ý nghĩa tuyệt đối.
2. *Nguy cơ thiên lệch người chấm (Evaluator Bias):* Tác giả bài làm đồng thời là người thực hiện chấm thủ công Coherence và Grounding. Dù đã tuân thủ thang tiêu chí nghiêm ngặt trong GUIDE.md, vẫn tồn tại rủi ro thiên lệch chủ quan.
3. *Đo lường tài nguyên:* Thời gian chạy được đo trên phần cứng máy cá nhân (Windows, CPU Intel), có thể dao động nhẹ theo trạng thái tải nền của hệ điều hành.

---

### 5. Đề xuất cải tiến khi làm lại hoặc mở rộng

1. **Hybrid Retrieval (Dense + BM25 Sparse Search):** Kết hợp vector đa ngữ của Sentence Transformers với thuật toán từ khóa BM25 để vừa bắt được ngữ nghĩa khái quát, vừa bắt chính xác các con số điều kiện đặc thù (như "50%", "3.60", "23h00").
2. **Hierarchical / Parent-Document Retrieval:** Chia chunk nhỏ 200–300 ký tự để tìm kiếm vector chính xác cao, nhưng khi gửi bằng chứng cho LLM thì trả về toàn bộ Điều (Parent Chunk 800–1.000 ký tự) để đảm bảo 100% tính mạch lạc và đầy đủ điều kiện ngoại lệ.
3. **Phân loại câu hỏi tự động (Query Intent & Metadata Routing):** Áp dụng một mô hình phân loại nhẹ hoặc rule-based router để tự động trích xuất `section` từ câu hỏi tự nhiên của sinh viên trước khi truyền vào vector store.
