# Day 04 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. Xong trước 11:30 để làm tài liệu phụ trợ khi demo.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. Có thể hoàn thiện sau buổi debate để nộp bài.

## Team

- Team: G14-E403
- Members: HoangDuyLinh
- Provider/model: OpenRouter / Llama-3 (hoặc tuỳ chọn trong .env)

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research agent thông minh: tự động định tuyến (routing) linh hoạt để tìm kiếm tin tức trên Web và Twitter, tra cứu báo cáo khoa học, và dịch thuật. Agent được trang bị cơ chế an toàn cực cao: biết tự đặt câu hỏi làm rõ (clarify) khi thiếu thông tin và luôn xin phép trước khi gửi dữ liệu ra ngoài.

**Link dùng thử (truy cập được trong showdown):**

> URL: http://localhost:8501

## A2. Tool agent có

> Các công cụ (tools) mà Agent được trang bị để thực hiện tác vụ:

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | Hỏi lại người dùng khi thiếu thông tin hoặc cần xin phép | Không |
| lookup | Tra cứu thông tin, tin tức thời sự trên Internet | Không |
| social_search | Tìm kiếm các bài đăng, xu hướng trên mạng xã hội | Không |
| timeline | Trích xuất các bài đăng gần đây của một người dùng cụ thể | Không |
| fetch | Truy cập và đọc trực tiếp nội dung từ một URL cụ thể | Không |
| format | Trình bày và định dạng lại văn bản báo cáo | Không |
| send | Gửi tin nhắn ra ngoài (ví dụ: Telegram) - Đòi hỏi xác nhận | Không |
| policy | Tra cứu quy định, tài liệu nội bộ | Không |
| papers | Tìm kiếm báo cáo khoa học (Arxiv) | Không |
| paper_text | Đọc nội dung chi tiết của một bài báo cáo khoa học | Không |
| translate | Dịch đoạn văn bản sang ngôn ngữ khác theo yêu cầu | **Có (Bắt buộc)** |
| youtube_summarizer | Trích xuất và tóm tắt nội dung video Youtube từ link | **Có (VIP/Bonus)** |

## A3. Câu hỏi mẫu để thử

> 3 câu hỏi mẫu để team khác tự vọc vạch tính năng của Agent:

1. Tìm kiếm và tóm tắt tin tức mới nhất về trí tuệ nhân tạo (AI) trên web hôm nay.
2. Dịch đoạn văn bản này sang tiếng Hàn Quốc giúp mình. (Agent sẽ phản xạ hỏi "Đoạn văn bản nào?").
3. Hãy gửi bản báo cáo tin tức vừa tìm được lên nhóm Telegram giúp mình. (Agent sẽ cảnh báo và xin phép yes/no).

## A4. Kịch bản demo đã rehearse

> 3 kịch bản chạy thử nghiệm đã thao tác trên Chat Live (transcripts/):

| Scenario | Tool trace cần thấy | Câu chuyện cải thiện version | Fallback run/transcript |
|---|---|---|---|
| 1. Bình thường | `lookup()` -> kết quả | v0 thường nhầm lẫn, v1+v2 gọi chuẩn xác `lookup` theo ngữ cảnh. | v3_openrouter...transcript.json |
| 2. Thiếu thông tin | `clarify(text)` -> dịch | v0 hay tự bịa nội dung. Ở v2/v3, Agent bị ép vào khuôn khổ bắt buộc hỏi lại. | v3_openrouter...transcript.json |
| 3. Gửi tin (Boundary) | `clarify(yes_no)` | Trình diễn tính năng an toàn cốt lõi: tự chốt chặn việc rò rỉ dữ liệu khi chưa cho phép. | v3_openrouter...transcript.json |

---

# PHẦN B — Chi tiết / Bằng chứng

> Điều kiện metric hợp lệ: `provider_error_cases` phải bằng `0`; `measured_cases` phải bằng `total_cases`; và bất kỳ `tool_results` nào có error đều phải được review thủ công vì routing PASS không chứng minh tool execution đã đúng.

## B1. Version evidence

Fill from `artifacts/version_log.csv` and `runs/*.json`.

| Version | Prompt/tool change | Hypothesis | Metric name | Before | After | Run File |
|---|---|---|---|---:|---:|---|
| v0 | baseline |  |  |  |  |  |
| v1 |  |  |  |  |  |  |
| v2 |  |  |  |  |  |  |
| v3 |  |  |  |  |  |  |

## B2. Failure analysis

Use actual failures from `results[*].result.failures`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
|  |  |  |  |  |

## B3. Team eval cases

List the 10 cases added to `data/eval_group.json`:

- 5 single-turn
- 5 multi-turn

This section is for the mandatory team-authored eval set. Optional built-ins do
not belong here.

File template để trống có chủ đích; nhóm phải tự thiết kế đủ 10 case.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
|  |  |  |  |

## B4. Live chat evidence

Use `transcripts/*.transcript.json`.

| Scenario/Turn | Version | Tool Calls + Args | Transcript/Run | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B5. Tool capability evidence

Phân loại rõ tool mới bắt buộc, optional built-in và tool đủ điều kiện bonus. Chỉ ghi Telegram/PDF nếu nhóm thực sự dùng; base report không cần chúng.

UI is core deliverable, not bonus. Do not list it here.

| Category | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Must-have: tool mới đầu tiên | `tools/translate/` | Tích hợp thành công và pass ST_01/ST_04/MT_01 | LLM có thể gọi nhầm tool nếu prompt không rõ |
| Optional built-in | `tools/clarify/` | Đã xử lý triệt để missing_info (url, handle) và yes_no confirmation | Cần quy định rõ `response_type` trong system prompt |
| Bonus: tool VIP thứ 4 trở đi | `tools/youtube_summarizer/` | Xử lý được các đường link Youtube từ user để tóm tắt | Giới hạn dung lượng token nếu video quá dài |

## B6. Reflection

- Which fixes belonged in `system_prompt.md`?
- Which fixes belonged in `tools.yaml`?
- Which failure needed manual review instead of automatic grading?
- What would you improve next?
