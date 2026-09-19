# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Vũ Gia Khải  
**Mã sinh viên:** 2A202602786  
**Nhóm:** Nhóm PTIT — K4-L3A  
**Ngày:** 2026-09-19  

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine cao nghĩa là góc giữa hai vector biểu diễn văn bản trong không gian đa chiều rất nhỏ ($\cos \theta \approx 1$), thể hiện hai đoạn văn bản có sự tương đồng lớn về mặt ngữ nghĩa và hướng biểu diễn, bất kể độ dài ngắn của câu.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Sinh viên đăng ký học phần trực tuyến trên hệ thống quản lý đào tạo của Học viện."
- Câu B: "Người học thực hiện chọn môn học qua cổng thông tin đào tạo điện tử."
- Tại sao tương đồng: Hai câu cùng mô tả một nghiệp vụ (đăng ký môn học online tại cơ sở đào tạo) với các từ đồng nghĩa và cấu trúc tương đương ("sinh viên" ~ "người học", "học phần" ~ "môn học", "trực tuyến" ~ "điện tử").

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Thời hạn nộp đơn phúc khảo bài thi kết thúc học phần là 03 ngày làm việc."
- Câu B: "Nội quy ký túc xá nghiêm cấm sử dụng bếp điện và các chất dễ cháy nổ trong phòng ở."
- Tại sao khác: Hai câu thuộc hai phạm trù hoàn toàn độc lập (quy chế khảo thí học vụ vs an toàn sinh hoạt nội trú ký túc xá), không chia sẻ ngữ cảnh hay trường từ vựng chung.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Khoảng cách Euclid phụ thuộc trực tiếp vào độ lớn (magnitude/độ dài) của vector, khiến hai văn bản cùng một chủ đề nhưng một đoạn ngắn, một đoạn dài bị coi là cách rất xa nhau. Trong khi đó, Cosine similarity chuẩn hóa độ dài và chỉ đo góc định hướng của vector, phản ánh chính xác sự tương đồng ngữ nghĩa mà không bị sai lệch bởi độ dài văn bản.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*
> Áp dụng công thức: $\text{Số lượng chunk} = \lceil \frac{\text{độ\_dài} - \text{độ\_chồng\_chéo}}{\text{kích\_thước\_chunk} - \text{độ\_chồng\_chéo}} \rceil$  
> Thay số: $\lceil \frac{10000 - 50}{500 - 50} \rceil = \lceil \frac{9950}{450} \rceil = \lceil 22.111 \rceil = 23$  
> *Đáp án:* **23 chunks**

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Khi overlap tăng lên 100, số lượng chunk là: $\lceil \frac{10000 - 100}{500 - 100} \rceil = \lceil \frac{9900}{400} \rceil = \lceil 24.75 \rceil = 25$ chunks (tăng thêm 2 chunks).  
> Ta muốn tăng độ chồng chéo để duy trì tính liên tục của ngữ cảnh tại các ranh giới cắt, tránh việc một câu, mệnh đề điều kiện hoặc thực thể ngữ nghĩa quan trọng bị chia cắt giữa hai chunk dẫn đến mất ngữ cảnh khi tìm kiếm.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi sử dụng biểu thức chính quy với kỹ thuật lookbehind `re.split(r'(?<=[.!?])\s+|(?<=\.)\n+', text.strip())` nhằm nhận diện chính xác các dấu ngắt câu (`. `, `! `, `? `, `.\n`) mà không làm mất dấu câu ở cuối mệnh đề. Sau đó, code loại bỏ câu rỗng, gom từng nhóm tối đa `max_sentences_per_chunk` câu thành một chunk và làm sạch khoảng trắng (`strip()`). Trường hợp chuỗi đầu vào rỗng được xử lý trả về danh sách rỗng ngay từ đầu.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán đệ quy duyệt danh sách các ký tự phân tách theo thứ tự ưu tiên giảm dần: `["\n\n", "\n", ". ", " ", ""]`. Trường hợp cơ sở (base case) là khi văn bản có độ dài $\le$ `chunk_size` (trả về chính nó), hoặc khi danh sách separator rỗng thì fallback cắt cứng theo kích thước `chunk_size`. Khi một đoạn văn bản sau khi tách vẫn lớn hơn `chunk_size`, thuật toán tiếp tục gọi đệ quy với separator cấp kế tiếp, sau đó gom các đoạn nhỏ lại bằng separator tương ứng để tối ưu độ dài từng chunk.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Tôi chuẩn hóa mỗi Document thành một record gồm `id`, `content`, `embedding` (tính qua `_embedding_fn`) và `metadata`, sau đó lưu vào danh sách `self._store` (đồng thời đồng bộ sang ChromaDB nếu có). Với `search`, tôi nhúng query thành vector, tính tích vô hướng (dot product) giữa query vector và từng vector trong kho (vì vector đã được chuẩn hóa L2 nên dot product tương đương cosine similarity), sắp xếp giảm dần theo `score` và trả về top-k bản ghi.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Với `search_with_filter`, tôi áp dụng chiến lược tiền lọc (pre-filtering): duyệt qua kho bản ghi, chỉ giữ lại các chunk thỏa mãn toàn bộ các điều kiện key-value trong `metadata_filter`, sau đó mới chuyển tập ứng viên này vào hàm tìm kiếm tương đồng để lấy top-k. Hàm `delete_document` xóa tất cả bản ghi có `id == doc_id` hoặc `metadata['doc_id'] == doc_id` bằng list comprehension và trả về `True` nếu số lượng phần tử giảm xuống, ngược lại trả về `False`.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Hàm `answer` trước hết gọi `self.store.search(question, top_k=top_k)` để trích xuất các đoạn văn bản có độ tương đồng cao nhất. Sau đó, các đoạn văn này được ghép lại thành khối `Context:\n...` và truyền vào cấu trúc prompt RAG chuẩn: cung cấp ngữ cảnh trước, câu hỏi ở cuối và yêu cầu LLM đưa ra câu trả lời dựa trên ngữ cảnh đó thông qua hàm `self.llm_fn(prompt)`.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```text
============================= test session starts =============================
platform win32 -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\Admin\anaconda3\envs\DL\python.exe
cachedir: .pytest_cache
rootdir: D:\create\vin\K4-DAY07-Vu-Gia-Khai-2A202602786
plugins: anyio-4.13.0, langsmith-0.10.10
collecting ... collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================= 42 passed in 3.09s ==============================
```

**Số lượng bài test vượt qua (pass):** **42** / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|:---:|:------|:------|:-------:|:------------:|:-----:|
| 1 | Sinh viên đăng ký học phần trên hệ thống qldt của Học viện. | Học sinh đăng ký môn học trực tuyến qua cổng đào tạo. | cao | 0.0833 | Đúng |
| 2 | Thời hạn nộp đơn phúc khảo bài thi là trong vòng 03 ngày làm việc. | Sinh viên khiếu nại điểm thi kết thúc học phần trong 3 ngày. | cao | -0.2290 | Bất ngờ |
| 3 | Học bổng loại Xuất sắc yêu cầu điểm GPA từ 3.60 trở lên. | Nội quy ký túc xá nghiêm cấm nấu ăn bằng bếp điện trong phòng. | thấp | -0.0169 | Đúng |
| 4 | Sinh viên nợ học phí quá hạn sẽ bị cấm thi kết thúc học phần. | Thời gian mở cửa thư viện từ 07h30 sáng đến 21h00 tối. | thấp | 0.0436 | Đúng |
| 5 | Giảng viên phải hoàn thành việc chấm bài thi trong 07 ngày làm việc. | Cán bộ chấm thi nộp bảng điểm gốc và túi bài thi về Trung tâm Khảo thí. | cao | 0.0279 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Kết quả bất ngờ nhất là ở Cặp 2: hai câu mang nội dung ngữ nghĩa rất tương đồng về thủ tục phúc khảo trong 3 ngày nhưng lại có điểm tương tự âm (-0.2290). Điều này phản ánh rõ hạn chế của `MockEmbedder` (vốn sinh vector giả lập ngẫu nhiên dựa trên hash MD5 của chuỗi ký tự bề mặt). Trong thực tế, các mô hình embedding học sâu thực thụ (như multilingual Transformer) biểu diễn văn bản dựa trên không gian tiềm ẩn ngữ nghĩa, nên các câu dù khác biệt câu chữ nhưng cùng ngữ nghĩa sẽ được kéo lại gần nhau.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|:---|:---|:---|:---:|:---:|:---|
| 1 | Khối lượng học tập tối thiểu và tối đa sinh viên được đăng ký trong một học kỳ chính là bao nhiêu? | Quy định và Hướng dẫn Đăng ký học phần PTIT: Cử nhân tối thiểu 15 - tối đa 25 TC; Kỹ sư tối thiểu 16 - tối đa 25 TC... | 0.3105 | Có | Cử nhân 15-25 tín chỉ, Kỹ sư 16-25 tín chỉ, học lực yếu tối đa 14 tín chỉ. |
| 2 | Thời hạn nộp đơn phúc khảo bài thi kết thúc học phần là bao lâu và nộp ở đâu? | Quy định Phúc khảo bài thi kết thúc học phần: nộp trong 03 ngày làm việc kể từ ngày công bố điểm trên Slink... | 0.1058 | Có | Thời hạn 03 ngày làm việc trên ứng dụng Slink. |
| 3 | Điều kiện điểm GPA và điểm rèn luyện để đạt học bổng khuyến khích học tập loại Giỏi? | Quy định xét cấp Học bổng khuyến khích học tập: Loại Giỏi yêu cầu GPA từ 3.20 đến 3.59, điểm rèn luyện 80-89... | 0.0952 | Có | GPA từ 3.20 đến 3.59, điểm rèn luyện từ 80 đến 89 điểm (loại Tốt). |
| 4 | Sinh viên mượn sách thư viện tối đa được bao nhiêu cuốn và trong thời hạn bao lâu? | Nội quy Thư viện và Khai thác tài nguyên số PTIT: Sinh viên mượn tối đa 05 cuốn, thời hạn 14 ngày/lần... | 0.2118 | Có | Tối đa 05 cuốn sách, thời hạn 14 ngày, gia hạn 01 lần 07 ngày. |
| 5 | Quy định thời hạn giải quyết điểm thi và phúc khảo dành cho sinh viên là bao nhiêu ngày? *(có metadata_filter)* | `metadata_filter={'audience': 'student'}` trích xuất chính xác quy định phúc khảo học sinh viên trong 03 ngày, loại bỏ quy định nộp điểm 07 ngày của giảng viên. | 0.1454 | Có | Nộp đơn trong 03 ngày làm việc trên Slink, kết quả điều chỉnh nếu lệch từ 0.5 điểm trở lên. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** **5** / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Điều hay nhất là tác dụng rõ rệt của **Metadata Filtering (lọc tiền xử lý)**. Trong bộ quy chế đại học, cùng nói về "thời hạn điểm thi" nhưng giảng viên có thời hạn chấm 07 ngày, còn sinh viên có thời hạn phúc khảo 03 ngày. Nhờ bộ lọc `audience: student`, hệ thống đã loại bỏ hoàn toàn tài liệu gây nhiễu của giảng viên và cung cấp đúng thông tin sinh viên cần.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|:---|:---:|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |
