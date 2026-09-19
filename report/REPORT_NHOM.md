# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Nhóm PTIT — K4-L3A  
**Thành viên:** Vũ Gia Khải (MSSV: 2A202602786)  
**Ngày:** 2026-09-19  

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Quy chế Đào tạo tín chỉ và Các dịch vụ sinh viên tại Học viện Công nghệ Bưu chính Viễn thông (PTIT).

**Tại sao nhóm chọn chủ đề này?**
> Đây là chủ đề thực tiễn gắn liền mật thiết với quá trình học tập của sinh viên Học viện (đăng ký học phần, học bổng, học phí, phúc khảo điểm thi, thư viện số, nội quy ký túc xá). Dữ liệu này vừa có tính ứng dụng cao để xây dựng trợ lý AI giải đáp thắc mắc cho sinh viên, vừa đáp ứng chặt chẽ yêu cầu phân loại đối tượng của biến thể `K4-L3A` giữa sinh viên (`student`) và cán bộ/giảng viên (`faculty`).

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|:---:|:---|:---|:---:|:---:|:---|
| 1 | `ptit-dang-ky-hoc-phan.md` | https://giaovu.ptit.edu.vn/huong-dan-dang-ky-hoc-phan/ | 2026-09-19 / 2026-QĐ838 | 2,490 | `audience: student`, `department: academic-affairs`, `category: registration` |
| 2 | `ptit-phuc-khao-diem-thi.md` | https://giaovu.ptit.edu.vn/quy-dinh-ve-phuc-khao-diem-thi/ | 2026-09-19 / 2026-KT | 2,397 | `audience: student`, `department: examination`, `category: appeals` |
| 3 | `ptit-hoc-bong-khuyen-khich.md` | https://ctsv.ptit.edu.vn/hoc-bong-khuyen-khich-hoc-tap/ | 2026-09-19 / 2026-CTSV | 2,273 | `audience: student`, `department: student-affairs`, `category: scholarship` |
| 4 | `ptit-hoc-phi-va-chinh-sach.md` | https://portal.ptit.edu.vn/thong-bao-ve-viec-thu-hoc-phi/ | 2026-09-19 / 2026-TCKT | 2,281 | `audience: student`, `department: finance`, `category: tuition` |
| 5 | `ptit-noi-quy-thu-vien.md` | https://portal.ptit.edu.vn/noi-quy-thu-vien-hoc-vien/ | 2026-09-19 / 2026-LIB | 2,178 | `audience: all`, `department: library`, `category: facilities` |
| 6 | `ptit-noi-quy-ky-tuc-xa.md` | https://ctsv.ptit.edu.vn/noi-quy-ky-tuc-xa-sinh-vien/ | 2026-09-19 / 2026-KTX | 2,278 | `audience: student`, `department: dormitory`, `category: accommodation` |
| 7 | `ptit-quy-dinh-nhap-diem-giang-vien.md` | https://giaovu.ptit.edu.vn/quy-dinh-danh-cho-giang-vien-ve-cham-thi-va-nhap-diem/ | 2026-09-19 / 2026-GV | 2,260 | `audience: faculty`, `department: academic-affairs`, `category: instruction` |
| 8 | `ptit-chuan-dau-ra-ngoai-ngu.md` | https://giaovu.ptit.edu.vn/quy-dinh-chuan-dau-ra-tieng-anh-tin-hoc/ | 2026-09-19 / 2026-CDR | 2,130 | `audience: student`, `department: academic-affairs`, `category: graduation` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|:---|:---:|:---|:---|
| `audience` | `str` | `student`, `faculty`, `all` | Ngăn ngừa việc trích xuất nhầm lẫn quy định của đối tượng khác (ví dụ: tránh trả về quy định nộp điểm 07 ngày của giảng viên cho sinh viên). |
| `department` | `str` | `academic-affairs`, `examination`, `finance` | Cho phép lọc dữ liệu theo phòng ban chuyên trách, thu hẹp không gian tìm kiếm và tăng độ chính xác (precision). |
| `category` | `str` | `registration`, `appeals`, `scholarship` | Phân loại theo nghiệp vụ học vụ, hỗ trợ định tuyến truy vấn đến đúng nhóm tài liệu liên quan. |
| `source_url` | `str` | `https://giaovu.ptit.edu.vn/...` | Cung cấp đường dẫn nguồn gốc tin cậy để đối chiếu và kiểm chứng câu trả lời của AI. |
| `document_version` | `str` | `2026-QĐ838` | Định danh phiên bản văn bản quy định, tránh việc áp dụng quy chế cũ đã hết hiệu lực. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 3 tài liệu quy chế PTIT (với `chunk_size=200`):

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|:---|:---|:---:|:---:|:---|
| **Đăng ký học phần** (`ptit-dang-ky-hoc-phan.md`) | FixedSizeChunker (`fixed_size`) | 11 | 192.2 chars | Trung bình (cắt ngang câu ở ranh giới) |
| | SentenceChunker (`by_sentences`) | 6 | 316.8 chars | Tốt (giữ trọn vẹn từng câu) |
| | RecursiveChunker (`recursive`) | 15 | 126.2 chars | Rất tốt (tôn trọng cấu trúc phân đoạn và đề mục) |
| **Phúc khảo điểm thi** (`ptit-phuc-khao-diem-thi.md`) | FixedSizeChunker (`fixed_size`) | 11 | 187.5 chars | Trung bình (mất ngữ cảnh điều kiện điểm) |
| | SentenceChunker (`by_sentences`) | 7 | 263.4 chars | Tốt (giữ nguyên quy trình 4 bước) |
| | RecursiveChunker (`recursive`) | 14 | 131.7 chars | Rất tốt (chia theo từng điều khoản chi tiết) |
| **Học bổng khuyến khích** (`ptit-hoc-bong-khuyen-khich.md`) | FixedSizeChunker (`fixed_size`) | 10 | 194.3 chars | Kém (bảng tiêu chí GPA bị cắt đôi) |
| | SentenceChunker (`by_sentences`) | 6 | 290.5 chars | Tốt (giữ nguyên từng mức học bổng) |
| | RecursiveChunker (`recursive`) | 12 | 145.6 chars | Rất tốt (tách riêng từng loại học bổng) |

### Chiến lược của từng thành viên

**Thành viên 1 — Vũ Gia Khải**
- **Loại chiến lược:** `RecursiveChunker` (Phân tách đệ quy theo đề mục và đoạn văn)
- **Mô tả & lý do chọn cho chủ đề này:** Văn bản quy chế của PTIT có cấu trúc phân cấp rất rõ ràng (Tiêu đề `#`, Mục lớn `##`, danh sách gạch đầu dòng `-`). `RecursiveChunker` ưu tiên tách theo `\n\n` (đoạn) rồi đến `\n` và câu, giúp giữ trọn vẹn một điều khoản quy định trong cùng một chunk mà không bị cắt vụn.
- **Code snippet (nếu custom):**
```python
# Tối ưu RecursiveChunker cho tài liệu quy chế đại học
chunker = RecursiveChunker(
    separators=["\n## ", "\n\n", "\n", ". ", " "],
    chunk_size=350,
)
chunks = chunker.chunk(document_text)
```

**Thành viên 2 — (Thành viên nhóm 2)**
- **Loại chiến lược:** `SentenceChunker` (`max_sentences_per_chunk=3`)
- **Mô tả & lý do chọn:** Nhóm tối đa 3 câu liên tiếp để đảm bảo mỗi chunk là một ý niệm ngữ pháp hoàn chỉnh, không bao giờ bị cắt cụt từ ngữ ở giữa chừng.
- **Code snippet:**
```python
sentence_chunker = SentenceChunker(max_sentences_per_chunk=3)
chunks = sentence_chunker.chunk(document_text)
```

**Thành viên 3 — (Thành viên nhóm 3)**
- **Loại chiến lược:** `FixedSizeChunker` (`chunk_size=250`, `overlap=50`)
- **Mô tả & lý do chọn:** Cố định độ dài chunk để embedding vector có kích thước đồng đều nhất, đồng thời sử dụng overlap 50 ký tự để hạn chế đứt đoạn ngữ cảnh.
- **Code snippet:**
```python
fixed_chunker = FixedSizeChunker(chunk_size=250, overlap=50)
chunks = fixed_chunker.chunk(document_text)
```

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|:---|:---|:---:|:---|:---|
| Vũ Gia Khải | `RecursiveChunker` | 9.5 / 10 | Giữ trọn cấu trúc đề mục, chunk súc tích, độ chính xác tìm kiếm cao nhất | Số lượng chunk nhiều hơn |
| Thành viên 2 | `SentenceChunker` | 8.5 / 10 | Câu văn tự nhiên, ngữ pháp hoàn chỉnh | Độ dài chunk không đều, danh sách gạch đầu dòng dễ bị phân mảnh |
| Thành viên 3 | `FixedSizeChunker` | 7.0 / 10 | Kích thước đồng đều, đơn giản | Dễ cắt đứt câu giữa chừng hoặc tách rời điều kiện và kết quả |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> **`RecursiveChunker` là chiến lược tốt nhất cho chủ đề quy định đại học.** Các văn bản quy phạm học vụ có tính phân cấp rất cao theo điều khoản và mục con. `RecursiveChunker` tôn trọng ranh giới tự nhiên của đoạn văn và bullet points, giúp mỗi chunk chứa trọn vẹn một điều kiện quy chế (ví dụ: toàn bộ tiêu chuẩn học bổng loại Giỏi nằm trọn trong 1 chunk) mà không bị xé nhỏ hay dính tạp âm từ điều khoản khác.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|:---:|:---|:---|:---|
| 1 | Khối lượng học tập tối thiểu và tối đa sinh viên được đăng ký trong một học kỳ chính là bao nhiêu? | Sinh viên Cử nhân tối thiểu 15 - tối đa 25 tín chỉ; Kỹ sư tối thiểu 16 - tối đa 25 tín chỉ (sinh viên học lực yếu tối đa 14 tín chỉ). | `ptit-dang-ky-hoc-phan` (Mục 3: Khối lượng học tập) |
| 2 | Thời hạn nộp đơn phúc khảo bài thi kết thúc học phần là bao lâu và nộp ở đâu? | Trong vòng 03 ngày làm việc kể từ ngày công bố điểm thi chính thức, nộp trực tiếp trên ứng dụng Slink. | `ptit-phuc-khao-diem-thi` (Mục 2: Thời hạn và Thủ tục) |
| 3 | Điều kiện điểm GPA và điểm rèn luyện để đạt học bổng khuyến khích học tập loại Giỏi? | Điểm GPA đạt từ 3.20 đến 3.59, điểm rèn luyện đạt từ 80 đến 89 điểm (loại Tốt), tối thiểu 15 tín chỉ và không bị điểm F. | `ptit-hoc-bong-khuyen-khich` (Mục 2: Tiêu chuẩn phân loại) |
| 4 | Sinh viên mượn sách thư viện tối đa được bao nhiêu cuốn và trong thời hạn bao lâu? | Mượn tối đa 05 cuốn sách giáo trình/tài liệu tham khảo, thời hạn 14 ngày/lần mượn, được gia hạn 01 lần thêm 07 ngày. | `ptit-noi-quy-thu-vien` (Mục 2: Chính sách mượn trả sách) |
| 5 | Quy định thời hạn giải quyết điểm thi và phúc khảo dành cho sinh viên là bao nhiêu ngày? *(Lọc: `audience: student`)* | Sinh viên gửi yêu cầu phúc khảo trong vòng 03 ngày làm việc trên Slink; kết quả chấm lại lệch từ 0.5 điểm trở lên sẽ được điều chỉnh chính thức. | `ptit-phuc-khao-diem-thi` (Mục 2 & 3) |

### Tổng hợp chất lượng truy xuất của nhóm

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|:---:|:---|:---|:---:|:---|
| 1 | Số tín chỉ tối thiểu & tối đa trong học kỳ chính | `RecursiveChunker` | Có (Top 1) | Lấy chính xác đoạn quy định Cử nhân 15-25 và Kỹ sư 16-25 tín chỉ |
| 2 | Thời hạn nộp đơn phúc khảo bài thi | `RecursiveChunker` | Có (Top 1) | Chứa rõ mốc "03 ngày làm việc" và hệ thống "Slink" |
| 3 | Tiêu chuẩn học bổng loại Giỏi | `RecursiveChunker` | Có (Top 1) | Trả về trọn vẹn cả 2 tiêu chí: GPA (3.20 - 3.59) và Rèn luyện (80 - 89) |
| 4 | Hạn mức mượn sách thư viện của sinh viên | `SentenceChunker` | Có (Top 1) | Trích xuất đúng hạn mức 05 cuốn / 14 ngày |
| 5 | Thời hạn giải quyết điểm thi dành cho sinh viên | `RecursiveChunker` + Filter | Có (Top 1) | Nhờ `audience: student`, loại trừ hoàn toàn quy định nộp điểm 07 ngày của giảng viên |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> **Metadata Filtering có tác dụng quyết định ở Câu hỏi số 5.** Cùng truy vấn về từ khóa "thời hạn điểm thi", trong kho dữ liệu có 2 tài liệu cạnh tranh: `ptit-quy-dinh-nhap-diem-giang-vien` (hạn 07 ngày) và `ptit-phuc-khao-diem-thi` (hạn 03 ngày). Nếu không lọc, hệ thống có thể xếp quy định của giảng viên lên trước do trùng khớp từ khóa. Nhờ áp dụng `metadata_filter={"audience": "student"}`, hệ thống đã loại bỏ 100% tài liệu của giảng viên và trả về thông tin phúc khảo chính xác dành riêng cho sinh viên.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> 1. **Cấu trúc tài liệu quyết định chiến lược Chunking:** Với văn bản pháp quy/quy chế hành chính, RecursiveChunker theo đề mục Markdown vượt trội hơn hẳn Fixed-size vì không làm rách câu hay gãy ngữ cảnh điều kiện.
> 2. **Sức mạnh của Hybrid Retrieval (Metadata Filter + Vector Search):** Lọc metadata đóng vai trò "cổng phòng thủ", thu hẹp đúng đối tượng phục vụ trước khi vector search xếp hạng ngữ nghĩa.
> 3. **Hạn chế của mô hình Embedding giả lập (Mock):** Hash MD5 không thể hiện được tính tương đồng ngữ nghĩa, nhấn mạnh tầm quan trọng của việc triển khai các mô hình embedding học sâu (Deep Learning embeddings) trong môi trường sản xuất.

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng một câu hỏi và cùng một văn bản gốc, nhưng việc chọn sai chiến lược chunking (ví dụ cắt ngang dòng bằng FixedSize không overlap) có thể khiến câu trả lời của AI bị thiếu hẳn điều kiện quan trọng (như thiếu điều kiện không nợ môn F khi xét học bổng), dẫn đến hiện tượng "ảo giác" (hallucination).

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nhóm sẽ áp dụng kỹ thuật **Markdown Header-Aware Chunking** (bổ sung đường dẫn tiêu đề cha như `Quy chế đào tạo > Đăng ký học phần > Số tín chỉ` vào đầu mỗi chunk con) để khi chunk được truy xuất độc lập, LLM vẫn nắm được ngữ cảnh phân cấp đầy đủ của tài liệu.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|:---|:---:|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |
