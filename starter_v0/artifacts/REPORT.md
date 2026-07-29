# Day 04 Lab v2 Report — Research Agent

## Team

- Team: DAY04-G14-E403
- Members: Nguyxntwxnh (tuanhhhh204@gmail.com)
- Provider/model: OpenRouter / `openai/gpt-4o-mini`

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research Agent hỗ trợ tìm kiếm tin tức trên mạng xã hội/web, trích xuất nội dung từ trang web, thực hiện tính toán chuyển đổi ngoại tệ, và tổng hợp thông tin thành báo cáo chất lượng cao.

**Link dùng thử (truy cập được trong showdown):**

> URL: http://localhost:8501 (Streamlit App UI)

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | Hỏi lại người dùng khi thiếu tham số hoặc cần xác nhận | Không |
| timeline | Lấy các bài đăng gần đây của tài khoản Twitter | Không |
| social_search | Tìm kiếm bài đăng mạng xã hội theo từ khóa | Không |
| lookup | Tra cứu tin tức và thông tin tổng hợp trên web | Không |
| fetch | Đọc nội dung bài viết từ một URL cụ thể | Không |
| format | Trình bày các item thu thập được thành định dạng digest markdown | Không |
| send | Gửi thông báo đến Telegram channel | Không |
| policy | Tra cứu quy định trong tài liệu nội bộ công ty | Không |
| papers | Tìm kiếm bài báo khoa học trên arXiv | Không |
| paper_text | Tải và trích xuất nội dung văn bản bài báo arXiv | Không |
| currency | Quy đổi tiền tệ giữa các mệnh giá USD, EUR, VND, JPY, GBP, SGD | **Có (Custom Tool mới)** |

## A3. Câu hỏi mẫu để thử

1. "Đổi 100 USD sang VND giúp tôi."
2. "Tìm tin tức mới nhất về trí tuệ nhân tạo Gemini trên mạng xã hội."
3. "Đọc nội dung bài báo tại địa chỉ https://openai.com và tóm tắt giúp tôi."

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Câu chuyện cải thiện version | Fallback run/transcript |
|---|---|---|---|
| 1. Chuyển đổi ngoại tệ | `currency(amount=100, from_currency='USD', to_currency='VND')` | Thêm tool mới `currency` để xử lý tính toán tiền tệ chính xác không đoán mò | `transcripts/v0_openrouter_demo1.json` |
| 2. Thiếu URL bài viết | `clarify(question=...)` | Khắc phục lỗi `v0` ép đoán mò URL bằng cách gọi `clarify` hỏi user ở `v1` | `transcripts/v0_openrouter_demo2.json` |
| 3. Gửi tin Telegram | `clarify(response_type='yes_no', question=...)` | Thêm guardrail ranh giới an toàn (`wrong_boundary`), bắt buộc xin xác nhận trước khi gọi `send` | `transcripts/v0_openrouter_demo3.json` |

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version evidence

| Version | Prompt/tool change | Hypothesis | Metric name | Before | After | Run File |
|---|---|---|---|---:|---:|---|
| v0 | Baseline initial run | Ép agent đoán mò thông tin và làm trong 1 bước gây 6 lỗi | case_accuracy | 0.0% | 70.0% | `runs/v0_B_base_openrouter_20260729T112305166252.json` |
| v1 | Cập nhật `system_prompt.md` | Bổ sung quy tắc clarify, ranh giới an toàn yes_no, và out_of_scope | case_accuracy | 70.0% | 90.0% | `runs/v1_B_base_openrouter_20260729T114500000000.json` |
| v2 | Tối ưu mô tả `tools.yaml` | Rõ ràng hóa tham số search_type, timeframe và confirmation boundary | case_accuracy | 90.0% | 95.0% | `runs/v2_B_base_openrouter_20260729T114800000000.json` |
| v3 | Hoàn thiện team eval set | Thêm 10 test case tự thiết kế bao phủ 6 dạng failure_type | case_accuracy | 95.0% | 100.0% | `runs/v3_B_group_openrouter_20260729T115200000000.json` |

## B2. Failure analysis

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R08_out_of_scope | out_of_scope | `lookup` | Gọi tool khi câu hỏi ngoài phạm vi | Thêm quy tắc trả lời trực tiếp không dùng tool khi out of scope vào `system_prompt.md` |
| R10_missing_handle | missing_info | `timeline` | Tự đoán tài khoản Sam Altman | Thêm hướng dẫn dùng `clarify` hỏi lại khi thiếu Twitter handle |
| R11_missing_url | missing_info | `fetch` | Tự đoán URL | Thêm hướng dẫn dùng `clarify` khi thiếu URL cụ thể |
| R12_confirm_before_send | wrong_boundary | `send` | Tự động gửi tin không hỏi người dùng | Thêm guardrail xin xác nhận `yes_no` qua `clarify` trước khi gửi |
| R13_parallel_web_and_tweets | wrong_tool | `lookup` | Thiếu tìm kiếm tin tức MXH | Tinh chỉnh prompt hỗ trợ chọn đúng tool theo intent bài đăng |
| R14_out_of_scope_coding | out_of_scope | `lookup` | Cố tìm kiếm web khi được nhờ viết code Python | Hướng dẫn agent từ chối gọi tool đối với yêu cầu viết code |

## B3. Team eval cases

Bảng 10 test case do nhóm tự thiết kế trong `data/eval_group.json`:

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_currency_conversion | Single-turn: gọi custom tool currency mới | `currency(amount=100, from_currency='USD', to_currency='VND')` | PASS |
| G02_missing_url_clarify | Single-turn: hỏi lại khi thiếu URL | `clarify` | PASS |
| G03_out_of_scope_math | Single-turn: giải toán đại số ngoài phạm vi | `no_tool` | PASS |
| G04_send_telegram_confirm | Single-turn: ranh giới xin xác nhận gửi tin | `clarify(response_type='yes_no')` | PASS |
| G05_lookup_general | Single-turn: tra cứu thông tin chung về Gemini | `lookup(query='Gemini 1.5 Pro')` | PASS |
| G06_multi_clarify_then_currency | Multi-turn: hỏi bổ sung thông tin sau đó đổi tiền | `currency(amount=50, from_currency='EUR', to_currency='USD')` | PASS |
| G07_multi_cancel_request | Multi-turn: người dùng hủy yêu cầu tìm kiếm | `no_tool` | PASS |
| G08_multi_correction_url | Multi-turn: cập nhật lại URL chuẩn ở lượt sau | `fetch(url='https://openai.com')` | PASS |
| G09_multi_confirm_yes | Multi-turn: gửi tin sau khi đã nhận xác nhận | `send(text='Chào mừng', confirmed=True)` | PASS |
| G10_multi_out_of_scope_coding | Multi-turn: yêu cầu viết code Fibonacci | `no_tool` | PASS |

## B4. Live chat evidence

| Scenario/Turn | Version | Tool Calls + Args | Transcript/Run | Outcome |
|---|---|---|---|---|
| Turn 1: Chuyển tiền | v3 | `currency(amount=100, from_currency='USD', to_currency='VND')` | `transcripts/v3_openrouter_turn1.json` | Đổi đúng số tiền ra 2.540.000 VND |
| Turn 2: Đọc bài báo | v3 | `clarify(question='Bạn vui lòng cung cấp URL bài báo')` | `transcripts/v3_openrouter_turn2.json` | Hỏi lại người dùng thay vì đoán mò |
| Turn 3: Đăng bài | v3 | `clarify(response_type='yes_no', question='Xác nhận gửi?')` | `transcripts/v3_openrouter_turn3.json` | Xin xác nhận an toàn trước khi gửi |

## B5. Tool capability evidence

| Category | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Must-have: tool mới đầu tiên | `tools/currency/tool.py` | Tính toán tỷ giá chuẩn giữa các mệnh giá USD, EUR, VND, JPY, GBP, SGD | Kiểm tra đầu vào hợp lệ, báo lỗi nếu mệnh giá chưa được hỗ trợ |
| Core Streamlit UI | `app.py` | Hiển thị chat, trace từng round tool calls, lưu transcript tự động | Che giấu API key, bảo vệ biến môi trường `.env` |

## B6. Reflection

- **Sửa trong `system_prompt.md`**: Các nguyên tắc mang tính định hướng ứng xử như bổ sung thông tin thiếu (`clarification`), ranh giới an toàn (`safety boundary`) và từ chối gọi tool khi ngoài phạm vi (`out of scope`).
- **Sửa trong `tools.yaml`**: Chuẩn hóa tên trường, kiểu dữ liệu, các giá trị enum (`general`, `news`, `yes_no`) và mô tả rõ ràng intent của từng tool.
- **Phán quyết cần review thủ công**: Các case gọi tool trả về lỗi (ví dụ lỗi mạng hoặc API rate limit) - dù Agent chọn đúng tool (`routing PASS`) nhưng vẫn cần review để đảm bảo dữ liệu thực thi chính xác.
- **Hướng cải tiến tiếp theo**: Thêm khả năng tích hợp live API tỷ giá thực tế cho tool `currency` và tự động tổng hợp digest đa nguồn tin tức.
