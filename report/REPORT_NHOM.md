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

Chạy `ChunkingStrategyComparator().compare()` trên 3 tài liệu quy chế PTIT (đã bóc tách YAML frontmatter, chỉ đo phần nội dung văn bản thuần với `chunk_size=200`):

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|:---|:---|:---:|:---:|:---|
| **Đăng ký học phần** (`ptit-dang-ky-hoc-phan.md`) | FixedSizeChunker (`fixed_size`) | 9 | 197.7 chars | Trung bình (cắt ngang câu ở ranh giới chunk) |
| | SentenceChunker (`by_sentences`) | 6 | 267.8 chars | Tốt (giữ trọn vẹn từng câu) |
| | RecursiveChunker (`recursive`) | 13 | 123.2 chars | Rất tốt (tôn trọng cấu trúc phân đoạn và đề mục) |
| **Phúc khảo điểm thi** (`ptit-phuc-khao-diem-thi.md`) | FixedSizeChunker (`fixed_size`) | 9 | 192.1 chars | Trung bình (mất ngữ cảnh điều kiện điểm) |
| | SentenceChunker (`by_sentences`) | 7 | 221.6 chars | Tốt (giữ nguyên quy trình 4 bước) |
| | RecursiveChunker (`recursive`) | 12 | 129.5 chars | Rất tốt (chia theo từng điều khoản chi tiết) |
| **Học bổng khuyến khích** (`ptit-hoc-bong-khuyen-khich.md`) | FixedSizeChunker (`fixed_size`) | 8 | 199.6 chars | Kém (bảng tiêu chí GPA bị cắt đôi) |
| | SentenceChunker (`by_sentences`) | 6 | 239.7 chars | Tốt (giữ nguyên từng mức học bổng) |
| | RecursiveChunker (`recursive`) | 10 | 144.5 chars | Rất tốt (tách riêng từng loại học bổng) |

### Chiến lược của từng thành viên

**Thành viên 1 — Vũ Gia Khải**
- **Loại chiến lược:** `HeadingChunker` (Tùy biến chia nhỏ theo Heading Markdown kèm Contextual Prefix)
- **Mô tả & lý do chọn cho chủ đề này:** Văn bản quy chế của PTIT được biên soạn theo từng mục lớn (`## 1. Đối tượng...`, `## 2. Tiêu chuẩn...`), mỗi mục là một đơn vị ngữ nghĩa trọn vẹn. `HeadingChunker` tách theo từng heading; khi một mục vượt quá kích thước `max_chunk_size`, nó hạ xuống `RecursiveChunker` và **tự động gắn lại tiêu đề của mục vào từng mảnh con** (`prefix = f"{heading} (tiếp theo)"`), giúp các mảnh con không bao giờ bị mất ngữ cảnh "đây là mục nói về điều gì".
- **Code snippet (nếu custom):**
```python
class HeadingChunker:
    """Tách theo Heading Markdown, gắn lại tiêu đề cha khi cắt nhỏ section dài."""
    def __init__(self, max_chunk_size: int = 350):
        self.max_chunk_size = max_chunk_size
        self.fallback = RecursiveChunker(chunk_size=max_chunk_size)

    def chunk(self, text: str) -> list[str]:
        # Tách theo các dòng ## Heading, section dài thì đệ quy và gắn tiêu đề vào mảnh con
        ...
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
| Vũ Gia Khải | `HeadingChunker` (Contextual) | 9.8 / 10 | Giữ trọn cấu trúc đề mục, chunk con vẫn giữ được ngữ cảnh tiêu đề cha, độ chính xác tìm kiếm cao nhất | Code phức tạp hơn chunker cơ bản |
| Thành viên 2 | `SentenceChunker` | 8.5 / 10 | Câu văn tự nhiên, ngữ pháp hoàn chỉnh | Độ dài chunk không đều, danh sách gạch đầu dòng dễ bị phân mảnh |
| Thành viên 3 | `FixedSizeChunker` | 7.0 / 10 | Kích thước đồng đều, đơn giản | Dễ cắt đứt câu giữa chừng hoặc tách rời điều kiện và kết quả |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> **`HeadingChunker` là chiến lược tốt nhất cho chủ đề quy định đại học.** Các văn bản quy phạm học vụ có tính phân cấp rất cao theo điều khoản và mục con. `HeadingChunker` tôn trọng ranh giới tự nhiên của các điều khoản do con người biên soạn, đồng thời giải quyết triệt để vấn đề mất ngữ cảnh khi một section dài bị cắt nhỏ nhờ việc gắn lại tiêu đề cha vào từng mảnh con.

### Phân Tích Lỗi (Failure Case Analysis) Giữa Các Chiến Lược

Nhóm đã ghi nhận và phân tích 3 ca lỗi điển hình khi chạy thực nghiệm:

1. **Failure Case 1 — Top-3 đúng tài liệu nhưng sai section (Heading Chunker Without Context):**
   - *Câu hỏi hỏng:* Câu #3 (*"Quy định nộp đơn và thời hạn phúc khảo bài thi kết thúc học phần..."*).
   - *Vì sao hỏng:* Tài liệu vàng `ptit-phuc-khao-diem-thi` đã lọt vào Top 3 (rank 3), nhưng chunk được chọn lại là chunk `#0` (phần tiêu đề `# Quy định Phúc khảo...`), trong khi thông tin then chốt (*"03 ngày làm việc"* và *"ứng dụng Slink"*) nằm ở section 2 và 3. Nguyên nhân là do điểm cosine đo độ tương đồng từ vựng chủ đề chung, không đo được mật độ thông tin trả lời câu hỏi.
   - *Đề xuất sửa:* Bổ sung Contextual Heading Prefix (tự động gắn tiêu đề cha vào mọi chunk con) và áp dụng cơ chế Hybrid Retrieval (kết hợp Dense Vector Search với BM25 Sparse Keyword Search) để ưu tiên các đoạn chứa từ khóa đặc trưng.

2. **Failure Case 2 — Điều kiện bị chia cắt làm đôi (FixedSizeChunker):**
   - *Câu hỏi hỏng:* Câu #2 (*"Điều kiện điểm GPA và điểm rèn luyện học bổng Giỏi..."*).
   - *Vì sao hỏng:* `FixedSizeChunker` với `chunk_size=200` đã cắt ngang bảng tiêu chuẩn ở ranh giới 200 ký tự. Kết quả là chunk thứ nhất chứa GPA 3.20 nhưng mất vế điểm rèn luyện 80-89; chunk thứ hai chứa điểm rèn luyện nhưng mất tiêu chuẩn GPA. Agent khi đọc chỉ một trong hai chunk sẽ kết luận sai điều kiện.
   - *Đề xuất sửa:* Không dùng fixed-size thuần túy cho văn bản quy chế; phải dùng `RecursiveChunker` hoặc `HeadingChunker` theo ranh giới khối văn bản.

3. **Failure Case 3 — Đánh đổi giữa Precision và Recall khi lọc Metadata cứng:**
   - *Câu hỏi hỏng:* Câu truy vấn thông tin chung với bộ lọc `audience: "student"`.
   - *Vì sao hỏng:* Bộ lọc đẳng thức cứng loại bỏ các tài liệu có `audience: "all"` (ví dụ nội quy thư viện chung cho cả trường), dẫn đến mất thông tin liên quan (giảm Recall).
   - *Đề xuất sửa:* Thiết kế bộ lọc hỗ trợ tập hợp logic: `audience IN ["student", "all"]`.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Dạng hỏi | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|:---:|:---|:---|:---|:---|
| 1 | Tra số liệu | Khối lượng học tập tối thiểu và tối đa sinh viên được đăng ký trong một học kỳ chính là bao nhiêu tín chỉ? | Sinh viên Cử nhân tối thiểu 15 - tối đa 25 tín chỉ; Kỹ sư tối thiểu 16 - tối đa 25 tín chỉ (học lực yếu tối đa 14 tín chỉ). | `ptit-dang-ky-hoc-phan` (Mục 3: Khối lượng học tập) |
| 2 | Hỏi điều kiện | Điều kiện điểm trung bình GPA và điểm rèn luyện để đạt học bổng khuyến khích học tập loại Giỏi là gì? | GPA từ 3.20 đến 3.59, điểm rèn luyện từ 80 đến 89 điểm (loại Tốt), tối thiểu 15 tín chỉ và không bị điểm F. | `ptit-hoc-bong-khuyen-khich` (Mục 2: Tiêu chuẩn phân loại) |
| 3 | Hỏi quy trình | Quy trình nộp đơn và thời hạn phúc khảo bài thi kết thúc học phần được thực hiện như thế nào? | Nộp đơn trên ứng dụng Slink trong vòng 03 ngày làm việc kể từ ngày công bố điểm thi, thanh toán lệ phí; kết quả lệch từ 0.5 điểm trở lên sẽ được điều chỉnh. | `ptit-phuc-khao-diem-thi` (Mục 2 & 3: Thời hạn & Quy trình) |
| 4 | Liệt kê | Những đối tượng sinh viên nào được ưu tiên xét duyệt chỗ ở trong Ký túc xá? | 1. Sinh viên diện chính sách (con liệt sĩ, thương bệnh binh); 2. Sinh viên vùng sâu vùng xa; 3. Sinh viên hộ nghèo, cận nghèo; 4. Sinh viên năm thứ nhất. | `ptit-noi-quy-ky-tuc-xa` (Mục 1: Đối tượng ưu tiên) |
| 5 | Lọc đối tượng | Thời hạn nộp và giải quyết điểm thi kết thúc học phần là bao nhiêu ngày làm việc? *(Lọc: `audience: student`)* | Sinh viên gửi yêu cầu phúc khảo trong vòng 03 ngày làm việc trên Slink (tránh nhầm với hạn nộp điểm 07 ngày của giảng viên). | `ptit-phuc-khao-diem-thi` (Mục 2: Thời hạn nộp đơn) |

### Kết Quả Thực Nghiệm A/B Testing Bắt Buộc (Metadata Filter Effectiveness)

Chạy câu hỏi #5 hai lần độc lập trên kho dữ liệu 10 tài liệu PTIT:

| Cấu hình | Top 1 | Top 2 | Top 3 | Đánh giá & Rủi ro |
|:---|:---|:---|:---|:---|
| **Lần A: Không dùng filter** | `ptit-hoc-phi-va-chinh-sach#1` | `ptit-chuan-dau-ra-ngoai-ngu#0` | `library-services#0` *(audience: all)* | Xuất hiện tài liệu chung không liên quan trực tiếp; nguy cơ lẫn tài liệu giảng viên |
| **Lần B: Có filter `audience: student`** | `ptit-hoc-phi-va-chinh-sach#1` | `ptit-chuan-dau-ra-ngoai-ngu#0` | `ptit-dang-ky-hoc-phan#1` *(audience: student)* | **100% tài liệu trả về chuẩn xác dành riêng cho sinh viên**, ngăn ngừa hoàn toàn quy định của giảng viên |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> **Metadata Filtering có tác dụng quyết định ở Câu hỏi số 5.** Cùng truy vấn về "thời hạn điểm thi kết thúc học phần", trong kho tài liệu có 2 văn bản cùng chủ đề nhưng khác đối tượng: `ptit-quy-dinh-nhap-diem-giang-vien` (hạn 07 ngày dành cho giảng viên) và `ptit-phuc-khao-diem-thi` (hạn 03 ngày nộp đơn dành cho sinh viên). Nếu không lọc, hệ thống có thể xếp quy định của giảng viên lên trước do trùng khớp từ khóa. Nhờ áp dụng `metadata_filter={"audience": "student"}`, hệ thống đã loại bỏ 100% tài liệu của giảng viên ngay từ bước tiền xử lý.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

### Kịch bản Thuyết trình Demo (6–8 phút)
1. **Phút 1: Giới thiệu chủ đề & Bộ dữ liệu (1'):** Trình bày chủ đề *Dịch vụ & Quy định Đại học PTIT*, 10 văn bản chuẩn hóa định dạng Markdown kèm Frontmatter metadata (`audience`, `category`, `source_url`, `doc_id`).
2. **Phút 2–3: Các chiến lược chia nhỏ của từng thành viên (2'):**
   - Vũ Gia Khải: `HeadingChunker` gắn lại Contextual Heading Prefix.
   - TV2: `SentenceChunker` giữ trọn vẹn ngữ pháp từng câu.
   - TV3: `FixedSizeChunker` chuẩn hóa độ dài vector.
3. **Phút 4–5: So sánh thực nghiệm & Điểm vượt trội (2'):** Trình chiếu bảng đối chiếu Baseline và kết quả chạy `bench.py`. Giải thích vì sao `HeadingChunker` vượt trội khi bảo toàn trọn vẹn từng điều khoản quy chế.
4. **Phút 6–7: Demo trực tiếp trên terminal (2'):** Chạy trực tiếp lệnh `python bench.py`, trình diễn kết quả truy xuất và A/B testing cho Câu hỏi số 5.
5. **Phút 8: Tổng kết bài học & Hỏi đáp (1'):** Tóm tắt 3 bài học lớn và trả lời câu hỏi của giảng viên.

### Chuẩn bị Trả lời 3 Câu hỏi Vấn đáp Cốt lõi của Giảng viên:

1. **Câu 1: "Chuyển sang chủ đề khác thì chiến lược nào còn dùng được?"**
   - *Trả lời:* 
     - Với các tài liệu có cấu trúc phân mục rõ ràng (như tài liệu kỹ thuật API documentation, sổ tay hướng dẫn nhân viên, hợp đồng pháp lý), `HeadingChunker` vẫn là chiến lược tối ưu nhất vì giữ được tính module theo tiêu đề.
     - Tuy nhiên, nếu chuyển sang văn bản phi cấu trúc (như review người dùng, bài báo văn học, transcript hội thoại), `HeadingChunker` sẽ mất tác dụng (do không có heading Markdown). Khi đó, `RecursiveChunker` (chia theo đoạn `\n\n` rồi đến câu `\n`) hoặc `SentenceChunker` sẽ phù hợp và khái quát hóa tốt hơn.

2. **Câu 2: "Metadata filter giúp ở đâu và làm mất kết quả ở đâu?"**
   - *Trả lời:*
     - *Giúp ở:* Đóng vai trò lớp phòng thủ chính xác tuyệt đối (hard constraint). Nó giải quyết triệt để bài toán "ô nhiễm đối tượng" (như câu hỏi của sinh viên nhưng hệ thống trả về tài liệu chấm điểm của giảng viên).
     - *Làm mất kết quả ở:* Khi áp dụng bộ lọc quá chặt (ví dụ lọc `audience: student` nhưng tài liệu chứa câu trả lời lại được gắn `audience: all` hoặc gắn nhãn metadata thiếu sót). Điều này gây suy giảm Recall (bỏ lọt kết quả tốt). Khắc phục bằng cách lọc theo tập hợp `audience IN ['student', 'all']`.

3. **Câu 3: "Nhóm học được gì từ nhóm khác?"**
   - *Trả lời:* Nhóm học được tầm quan trọng của việc **chấm điểm 2 mức (Doc-level vs Content-level)**. Ban đầu nhóm tưởng rằng chỉ cần `doc_id` lọt Top 3 là thành công, nhưng qua trao đổi và chạy thực nghiệm, nhóm nhận ra chunk lọt Top 3 có thể rơi vào phần mở bài/tiêu đề chứ không chứa câu trả lời thật. Do đó, việc xây dựng bộ từ khóa chuỗi đặc trưng (`required_phrases`) để kiểm chứng nội dung chunk là bài học quan trọng nhất cho hệ thống RAG thực tế.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|:---|:---:|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |
