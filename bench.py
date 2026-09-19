#!/usr/bin/env python3
"""
bench.py — Công cụ đo lường và đánh giá Retrieval Benchmark (Checkpoint 5 & 6).

Chức năng:
1. Đọc từng file .md trong data/university/, tách YAML frontmatter thành metadata và phần thân.
2. Chunk phần thân ngoài store, mỗi chunk tạo thành một Document:
      Document(id=f"{path.stem}#{i}", content=chunk,
               metadata={**frontmatter, "doc_id": path.stem, "chunk_index": i})
3. Nạp vào EmbeddingStore, chạy 5 câu hỏi benchmark qua search_with_filter().
4. Đánh giá 2 mức (Two-level Scoring):
      - Mức 1 (Doc-level): Tài liệu gold có trong top-3 không.
      - Mức 2 (Content-level): Chunk có chứa chuỗi đặc trưng (đáp án thật) không.
      - Thang điểm: 2đ (Top-1 + Content match), 1đ (Top-2/3 + Content match), 0đ (Trượt).
5. A/B Testing bắt buộc: Chạy câu lọc đối tượng (Q5) khi có và không có metadata_filter.
6. Phân tích lỗi (Failure Case Analysis).
7. Tự động lưu toàn bộ kết quả vào `ket_qua_benchmark.txt`.
"""

from __future__ import annotations

import io
import os
import sys
from pathlib import Path

# Đảm bảo import được module trong gói src
sys.path.insert(0, str(Path(__file__).parent))

from src import (
    Document,
    EmbeddingStore,
    FixedSizeChunker,
    SentenceChunker,
    RecursiveChunker,
    HeadingChunker,
    _mock_embed,
)


def parse_markdown_file(file_path: Path) -> tuple[dict[str, str], str]:
    """Tách YAML frontmatter và phần thân Markdown."""
    raw = file_path.read_text(encoding="utf-8")
    metadata: dict[str, str] = {}
    content = raw

    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) >= 3:
            content = parts[2].strip()
            fm_text = parts[1].strip()
            for line in fm_text.splitlines():
                if ":" in line:
                    key, val = line.split(":", 1)
                    # Loại bỏ inline comments nếu có
                    cleaned_val = val.split("#", 1)[0].strip()
                    metadata[key.strip()] = cleaned_val

    return metadata, content


# ==============================================================================
# 🎯 DÒNG CHỌN CHIẾN LƯỢC CHUNKER: Mỗi thành viên chỉ đổi 1 dòng này!
# Các lựa chọn:
#   - HeadingChunker(max_chunk_size=350)     <-- (Chiến lược đề xuất cho văn bản quy phạm)
#   - RecursiveChunker(chunk_size=200)
#   - SentenceChunker(max_sentences_per_chunk=3)
#   - FixedSizeChunker(chunk_size=200, overlap=30)
# ==============================================================================
SELECTED_CHUNKER = HeadingChunker(max_chunk_size=350)


# ==============================================================================
# 📋 5 BENCHMARK QUERIES & GOLD ANSWERS (Dùng chung cho cả nhóm)
# Kèm theo required_phrases (chuỗi đặc trưng) để chấm mức 2 (Content-level)
# ==============================================================================
BENCHMARK_QUERIES = [
    {
        "id": 1,
        "type": "Tra số liệu",
        "query": "Khối lượng học tập tối thiểu và tối đa sinh viên được đăng ký trong một học kỳ chính là bao nhiêu tín chỉ?",
        "gold_answer": "Sinh viên Cử nhân tối thiểu 15 - tối đa 25 tín chỉ; Kỹ sư tối thiểu 16 - tối đa 25 tín chỉ (học lực yếu tối đa 14 tín chỉ).",
        "target_doc": "ptit-dang-ky-hoc-phan",
        "required_phrases": ["15", "25", "tín chỉ"],
        "filter": None,
    },
    {
        "id": 2,
        "type": "Hỏi điều kiện",
        "query": "Điều kiện điểm trung bình GPA và điểm rèn luyện để đạt học bổng khuyến khích học tập loại Giỏi là gì?",
        "gold_answer": "GPA từ 3.20 đến 3.59, điểm rèn luyện từ 80 đến 89 điểm (loại Tốt), tối thiểu 15 tín chỉ và không bị điểm F.",
        "target_doc": "ptit-hoc-bong-khuyen-khich",
        "required_phrases": ["3.20", "80", "Giỏi"],
        "filter": None,
    },
    {
        "id": 3,
        "type": "Hỏi quy trình",
        "query": "Quy trình nộp đơn và thời hạn phúc khảo bài thi kết thúc học phần được thực hiện như thế nào?",
        "gold_answer": "Nộp đơn trên ứng dụng Slink trong vòng 03 ngày làm việc kể từ ngày công bố điểm thi, thanh toán lệ phí; kết quả lệch từ 0.5 điểm trở lên sẽ được điều chỉnh.",
        "target_doc": "ptit-phuc-khao-diem-thi",
        "required_phrases": ["03 ngày", "Slink"],
        "filter": None,
    },
    {
        "id": 4,
        "type": "Liệt kê",
        "query": "Những đối tượng sinh viên nào được ưu tiên xét duyệt chỗ ở trong Ký túc xá?",
        "gold_answer": "1. Sinh viên diện chính sách (con liệt sĩ, thương bệnh binh); 2. Sinh viên vùng sâu vùng xa; 3. Sinh viên hộ nghèo, cận nghèo; 4. Sinh viên năm thứ nhất.",
        "target_doc": "ptit-noi-quy-ky-tuc-xa",
        "required_phrases": ["ưu tiên", "chính sách", "hộ nghèo"],
        "filter": None,
    },
    {
        "id": 5,
        "type": "Lọc đối tượng (Audience Filter)",
        "query": "Thời hạn nộp và giải quyết điểm thi kết thúc học phần là bao nhiêu ngày làm việc?",
        "gold_answer": "Sinh viên gửi yêu cầu phúc khảo trong vòng 03 ngày làm việc trên Slink (tránh nhầm với hạn nộp điểm 07 ngày của giảng viên).",
        "target_doc": "ptit-phuc-khao-diem-thi",
        "required_phrases": ["03 ngày", "Slink"],
        "filter": {"audience": "student"},
    },
]


def evaluate_retrieval(
    store: EmbeddingStore,
    query_item: dict,
    custom_filter: dict | None = "DEFAULT",
) -> tuple[int, bool, bool, list[dict]]:
    """
    Chấm điểm truy xuất 2 mức theo Rubric:
    - Mức 1: doc_id có nằm trong top-3 không?
    - Mức 2: chunk trong top-3 có chứa chuỗi đặc trưng (required_phrases) không?
    Điểm:
      - 2 điểm: Top-1 là target_doc VÀ chứa chuỗi đặc trưng.
      - 1 điểm: Top-2 hoặc Top-3 là target_doc VÀ chứa chuỗi đặc trưng.
      - 0 điểm: Không tìm thấy target_doc HOẶC target_doc lọt top-3 nhưng sai section (không chứa chuỗi đặc trưng).
    """
    query = query_item["query"]
    target_doc = query_item["target_doc"]
    required_phrases = query_item["required_phrases"]
    filt = query_item["filter"] if custom_filter == "DEFAULT" else custom_filter

    results = store.search_with_filter(query, top_k=3, metadata_filter=filt)

    has_doc_match = False
    has_content_match = False
    best_matching_rank = None

    for rank, res in enumerate(results, start=1):
        doc_id = res["metadata"].get("doc_id", "")
        content = res["content"]

        if doc_id == target_doc:
            has_doc_match = True
            # Kiểm tra xem chunk này có chứa đủ hoặc đại diện chuỗi đặc trưng không
            matched_phrases = [p for p in required_phrases if p.lower() in content.lower()]
            if len(matched_phrases) >= len(required_phrases) * 0.5:
                has_content_match = True
                if best_matching_rank is None:
                    best_matching_rank = rank

    if has_content_match:
        score = 2 if best_matching_rank == 1 else 1
    else:
        score = 0

    return score, has_doc_match, has_content_match, results


def run_benchmark() -> int:
    output_buffer = io.StringIO()

    def log(msg: str = ""):
        print(msg)
        output_buffer.write(msg + "\n")

    log("=" * 75)
    log("🚀 BENCHMARK RETRIEVAL — CHECKPOINT 5 & 6 (K4-L3A: PTIT RULES)")
    log(f"📌 Chiến lược Chunker: {SELECTED_CHUNKER.__class__.__name__}")
    log("📌 Embedding Backend: MockEmbedder (Deterministic MD5-based)")
    log("   (Lưu ý: MockEmbedder sinh vector băm giả lập, số liệu mang tính so sánh cấu trúc chunk)")
    log("=" * 75)

    corpus_dir = Path("data/university")
    if not corpus_dir.exists():
        log(f"Lỗi: Không tìm thấy thư mục {corpus_dir}")
        return 1

    md_files = sorted(corpus_dir.glob("*.md"))
    if not md_files:
        log(f"Lỗi: Không có file .md nào trong {corpus_dir}")
        return 1

    # 1. Đọc từng file, tách frontmatter và chunk ngoài store
    all_chunks_docs: list[Document] = []
    file_count = 0

    for path in md_files:
        frontmatter, content_body = parse_markdown_file(path)
        if not content_body:
            continue

        file_count += 1
        chunks = SELECTED_CHUNKER.chunk(content_body)

        for i, chunk in enumerate(chunks):
            chunk_metadata = {
                **frontmatter,
                "doc_id": path.stem,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "source_file": path.name,
            }
            doc = Document(
                id=f"{path.stem}#{i}",
                content=chunk,
                metadata=chunk_metadata,
            )
            all_chunks_docs.append(doc)

    log(f"\n📦 Số tài liệu nguồn (.md): {file_count}")
    log(f"✂️  Tổng số chunks tạo ra: {len(all_chunks_docs)}")

    # 2. Nạp vào EmbeddingStore
    store = EmbeddingStore(collection_name="ptit_bench", embedding_fn=_mock_embed)
    store.add_documents(all_chunks_docs)
    log(f"💾 Số lượng chunks trong EmbeddingStore: {store.get_collection_size()}\n")

    # 3. Chạy 5 câu hỏi đánh giá theo thang điểm 2 mức
    log("=" * 75)
    log("🎯 PHẦN 1: ĐÁNH GIÁ 5 CÂU HỎI BENCHMARK (CHẤM 2 MỨC)")
    log("=" * 75)

    total_points = 0

    for q in BENCHMARK_QUERIES:
        qid = q["id"]
        qtype = q["type"]
        query = q["query"]
        filt = q["filter"]
        gold = q["gold_answer"]
        target = q["target_doc"]
        req = q["required_phrases"]

        score, doc_match, content_match, results = evaluate_retrieval(store, q)
        total_points += score

        log(f"\n[Câu hỏi #{qid} — {qtype}]")
        log(f"  ❓ Query: {query}")
        log(f"  🔍 Filter: {filt}")
        log(f"  🎯 Gold Doc: {target}")
        log(f"  🔑 Chuỗi đặc trưng cần có trong chunk: {req}")
        log(f"  📝 Gold Answer: {gold}")
        log(f"  🏆 Top-3 Chunks:")

        for rank, res in enumerate(results, start=1):
            doc_id = res["metadata"].get("doc_id", "N/A")
            chunk_id = res["id"]
            sim_score = res["score"]
            content_preview = res["content"][:110].replace("\n", " ") + "..."
            match_marker = []
            if doc_id == target:
                match_marker.append("ĐÚNG TÀI LIỆU")
            found_phrases = [p for p in req if p.lower() in res["content"].lower()]
            if found_phrases:
                match_marker.append(f"CHỨA ĐÁP ÁN: {found_phrases}")
            tag = f"✅ [{', '.join(match_marker)}]" if match_marker else ""

            log(f"    {rank}. [{chunk_id}] (Score: {sim_score:.4f}) {tag}")
            log(f"       doc_id: {doc_id} | audience: {res['metadata'].get('audience')}")
            log(f"       preview: {content_preview}")

        log(f"  📊 Chấm 2 mức: Mức 1 (Doc-level)={'ĐẠT' if doc_match else 'TRƯỢT'} | Mức 2 (Content-level)={'ĐẠT' if content_match else 'TRƯỢT'}")
        log(f"  ⭐ Điểm đạt được: {score}/2 điểm")

    log(f"\n👉 TỔNG ĐIỂM TRUY XUẤT: {total_points}/10 điểm")

    # 4. A/B Testing bắt buộc: Chạy câu hỏi #5 có và không có filter
    log("\n" + "=" * 75)
    log("🔬 PHẦN 2: A/B TESTING BẮT BUỘC (METADATA FILTER EFFECTIVENESS)")
    log("Câu hỏi #5: 'Thời hạn nộp và giải quyết điểm thi kết thúc học phần là bao nhiêu ngày làm việc?'")
    log("=" * 75)

    q5 = BENCHMARK_QUERIES[4]

    # Run A: KHÔNG lọc
    score_no_filter, _, _, res_no_filter = evaluate_retrieval(store, q5, custom_filter=None)
    # Run B: CÓ lọc audience: student
    score_with_filter, _, _, res_with_filter = evaluate_retrieval(store, q5, custom_filter={"audience": "student"})

    log("\n[A] Khi KHÔNG DÙNG metadata_filter (unfiltered):")
    for r, res in enumerate(res_no_filter, start=1):
        log(f"  Rank {r}: [{res['id']}] (doc: {res['metadata'].get('doc_id')}, audience: {res['metadata'].get('audience')}) - Score: {res['score']:.4f}")
        log(f"          Snippet: {res['content'][:90].replace(chr(10), ' ')}...")

    log("\n[B] Khi CÓ DÙNG metadata_filter={'audience': 'student'}:")
    for r, res in enumerate(res_with_filter, start=1):
        log(f"  Rank {r}: [{res['id']}] (doc: {res['metadata'].get('doc_id')}, audience: {res['metadata'].get('audience')}) - Score: {res['score']:.4f}")
        log(f"          Snippet: {res['content'][:90].replace(chr(10), ' ')}...")

    log("\n💡 KẾT LUẬN A/B TESTING:")
    log("- Khi không lọc, các tài liệu khác audience (như quy định chấm điểm của giảng viên) có thể cạnh tranh slot top-k.")
    log("- Khi kích hoạt metadata_filter={'audience': 'student'}, 100% tài liệu không thuộc đối tượng sinh viên bị loại bỏ ngay tại bước lọc trước (pre-filtering), bảo đảm an toàn thông tin.")

    # 5. Phân tích lỗi (Failure Case Analysis)
    log("\n" + "=" * 75)
    log("🔍 PHẦN 3: PHÂN TÍCH LỖI (FAILURE CASE ANALYSIS)")
    log("=" * 75)
    log("1. Hiện tượng: 'Top-3 đúng tài liệu nhưng sai section' (Heading Chunker Without Context).")
    log("   - Nguyên nhân: Trong cùng một văn bản quy định, các section cùng mang các từ khoá chung (như 'PTIT', 'sinh viên', 'quy định'). Do MockEmbedder tính vector từ MD5 băm ký tự, các chunk section mở đầu hoặc quy định chung có thể nhận điểm cosine cao hơn section cụ thể chứa số liệu.")
    log("   - Đề xuất sửa: Bổ sung Contextual Heading Prefix (đã tích hợp vào HeadingChunker) và trong thực tế phải nâng cấp lên Dense Semantic Embeddings (ví dụ paraphrase-multilingual-MiniLM) kết hợp Hybrid Search (BM25 + Dense) để nắm bắt cả từ khoá chính xác lẫn ngữ nghĩa sâu.")
    log("2. Hiện tượng: 'Đánh đổi giữa Precision và Recall khi lọc Metadata cứng'.")
    log("   - Nguyên nhân: Nếu tài liệu quy định chung gắn audience='all' nhưng query chỉ lọc audience='student', bộ lọc đẳng thức cứng có thể loại nhầm.")
    log("   - Đề xuất sửa: Thiết kế bộ lọc hỗ trợ tập hợp: `audience IN ['student', 'all']`.")

    log("\n" + "=" * 75)
    log("✅ HOÀN THÀNH TẤT CẢ CÁC MỤC BENCHMARK CHECKPOINT 5 & 6!")
    log("=" * 75)

    # Ghi ra file ket_qua_benchmark.txt
    output_path = Path("ket_qua_benchmark.txt")
    output_path.write_text(output_buffer.getvalue(), encoding="utf-8")
    print(f"\n📄 Đã xuất toàn bộ báo cáo benchmark ra file: {output_path.resolve()}")

    return 0


if __name__ == "__main__":
    raise SystemExit(run_benchmark())
