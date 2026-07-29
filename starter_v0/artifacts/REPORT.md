# Day 04 Lab v2 Report — Research Agent

## Team

- Team: G14-E403
- Members: chưa được cung cấp
- Provider/model: OpenRouter / `openai/gpt-4o-mini`

## PHẦN A — Giới thiệu agent

### A1. Agent này làm được gì

Research agent tìm tin trên web và mạng xã hội, đọc URL, tìm paper và tài liệu
nội bộ, sau đó có thể định dạng hoặc đăng kết quả lên Telegram sau khi người
dùng xác nhận.

Link dùng thử: chạy local bằng `chat.py`; chưa cấu hình public URL.

### A2. Tool agent có

| Tên tool | Làm được gì | Phân loại |
|---|---|---|
| `clarify` | Hỏi bổ sung dữ liệu hoặc xin xác nhận | core |
| `timeline` | Lấy bài đăng mới từ một tài khoản cụ thể | core |
| `social_search` | Tìm bài đăng theo chủ đề/từ khóa | core |
| `lookup` | Tìm thông tin hoặc tin tức trên web | core |
| `fetch` | Đọc một URL cụ thể | core |
| `format` | Định dạng danh sách kết quả thành digest | core |
| `send` | Đăng nội dung lên Telegram sau xác nhận | bonus, side effect |
| `policy` | Tìm trong tài liệu chính sách nội bộ | bonus |
| `papers` | Tìm paper khoa học | bonus |
| `paper_text` | Trích text từ paper | bonus |

### A3. Câu hỏi mẫu để thử

1. `Tweet mới nhất của Sam Altman là gì?`
2. `Tin tức AI hôm nay có gì nổi bật?`
3. `Tóm tắt bài này giúp mình: https://openai.com/blog/gpt-5`
4. `Tìm trên web tin robotics hôm nay và tìm thêm tweet về robotics.`
5. `Đăng bản tin này lên Telegram giúp mình.`

### A4. Kịch bản demo đã rehearse bằng eval

| Scenario | Tool trace cần thấy | Câu chuyện cải thiện | Run |
|---|---|---|---|
| Thiếu tài khoản | `clarify(response_type=text)` | v1 ngừng tự đoán `sama` | v1 base |
| Đăng Telegram | `clarify(response_type=yes_no)` | v2 thêm confirmation boundary | v2 base/group |
| Thiếu default argument | `clarify` có `response_type`; `lookup` có `topic/timeframe` | v3 siết schema | v3 base/group |
| Web + Twitter | `lookup` và `social_search` | v3 giữ đúng mọi source và argument | v3 group |

## PHẦN B — Chi tiết và bằng chứng

Điều kiện metric hợp lệ đều thỏa: mọi run chính có
`provider_error_cases=0` và `measured_cases=total_cases`.
Toàn bộ 110 case-row từ các run dùng trong báo cáo đã được flatten vào
`artifacts/run-analysis.csv`.

Manual review `tool_results`: case G07 ở v3 route đúng
`send(confirmed=true)` nhưng tool execution trả
`RuntimeError: Missing TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID`. Vì vậy điểm
100% của group là độ chính xác routing/arguments, không phải bằng chứng rằng tin
nhắn Telegram đã được gửi thành công.

### B1. Quy trình thí nghiệm tuần tự

```text
Chạy v0
→ đọc lỗi v0
→ đặt giả thuyết 1
→ sửa artifact
→ chạy v1
→ đọc lỗi v1
→ đặt giả thuyết 2
→ sửa artifact
→ chạy v2
→ đọc lỗi v2
→ đặt giả thuyết 3
→ sửa artifact
→ chạy v3
```

| Version | Thay đổi duy nhất | Giả thuyết hình thành từ version trước | Kết quả base | Kết quả group | Run |
|---|---|---|---:|---:|---|
| v0 | Baseline | Đo hành vi ban đầu | 65% | — | `runs/v0_B_base_openrouter_20260729T103030110043.json` |
| v1 | Prompt: hỏi lại khi thiếu account/URL, cấm bịa identifier | Lỗi R10/R11 đến từ chỉ dẫn đoán identifier | 95% | 70% | `runs/v1_B_base_openrouter_20260729T115625960375.json`, `runs/v1_B_group_openrouter_20260729T115729227058.json` |
| v2 | Prompt: confirmation boundary cho send/post/publish | Lỗi R12/G03 đến từ việc model tự suy diễn xác nhận | 95% | 80% | `runs/v2_B_base_openrouter_20260729T115944192547.json`, `runs/v2_B_group_openrouter_20260729T120043831332.json` |
| v3 | Tool schema: bắt buộc explicit `response_type`, `topic`, `timeframe` | Lỗi v2 cùng do model bỏ các field có default | 100% | 100% | `runs/v3_B_base_openrouter_20260729T120331931040.json`, `runs/v3_B_group_openrouter_20260729T120416132784.json` |

Ghi chú: v2 giữ nguyên base accuracy 95%, nhưng giả thuyết vẫn được xác nhận
trên targeted subset: R12 và G03 tăng từ 0/2 lên 2/2. Group accuracy tăng
70% lên 80%.

### B2. Phân tích lỗi theo từng vòng

| Version nguồn | Case | Quan sát thực tế | Giả thuyết tiếp theo / sửa |
|---|---|---|---|
| v0 | R10 | Tự chọn `timeline(screenname=sama)` khi thiếu account | v1: thiếu account phải `clarify(text)` |
| v0 | R11 | Tự bịa `https://example.com/article` | v1: thiếu URL phải `clarify(text)` |
| v0 | R12 | Gọi `send` trước xác nhận | Để lại, đọc lại sau v1 |
| v0 | R08, R14 | Dùng `send` cho câu ngoài phạm vi | Biến mất ở v1 như hiệu ứng phụ; không tuyên bố là giả thuyết chính |
| v0 | R13 | Tool thứ hai là `timeline(sama)` thay vì `social_search` | Biến mất ở v1 như hiệu ứng phụ của việc bỏ đoán account |
| v0 | R03 | `query="AI news"` thay vì `"AI"` | Không tái hiện ở v1; theo dõi regression |
| v1 | R12, G03 | Agent gọi `send`, thậm chí tự đặt `confirmed=true` | v2: cấm suy diễn confirmation; bắt buộc `clarify(yes_no)` |
| v1 | G09, G10 | Đúng query/timeframe nhưng thiếu `topic=news` | Để lại để xem sau v2 |
| v2 | R11, G01 | Đúng `clarify` nhưng bỏ `response_type=text` | v3: đặt `response_type` thành required |
| v2 | G09 | Đúng cả hai tool nhưng bỏ `lookup.topic=news` | v3: đặt `topic/timeframe` thành required |
| v3 | — | Không còn case fail | Kết thúc vòng; base và group đều 100% |

### B3. Mười eval case do nhóm tạo

File: `data/eval_group.json`.

| Case ID | Loại | Điều kiểm tra | Kết quả v3 |
|---|---|---|---|
| G01 | single | Thiếu account → `clarify(text)` | PASS |
| G02 | single | Coding ngoài phạm vi → no tool | PASS |
| G03 | single | Gửi Telegram → xác nhận trước | PASS |
| G04 | single | Tweet theo chủ đề → `social_search` | PASS |
| G05 | single | Query/topic/timeframe chính xác | PASS |
| G06 | multi | Carry URL rồi gọi `fetch` | PASS |
| G07 | multi | Chỉ `send(confirmed=true)` sau xác nhận | PASS |
| G08 | multi | Chuyển account timeline → topic search | PASS |
| G09 | multi | Carry chủ đề và gọi hai nguồn | PASS |
| G10 | multi | Sửa query, giữ topic/timeframe | PASS |

### B4. Live chat evidence

Chưa tạo transcript live chat trong vòng này. Bằng chứng hiện có là các run eval
JSON nêu ở B1; không ghi nhận transcript giả.

### B5. Tool capability evidence

| Category | Evidence | Kết quả | Guardrail |
|---|---|---|---|
| Core routing | v3 base/group | Đúng tool và argument 30/30 case | Missing identifier dùng `clarify` |
| Multi-source | G09 | Gọi cả `lookup` và `social_search` | Không bỏ source; explicit topic/timeframe |
| Side effect | R12, G03, G07 | Routing xác nhận đúng; G07 chưa gửi thật do thiếu Telegram env | Prompt boundary + runtime `confirmed` check |
| Argument contract | R11, G01, G09 | Không còn bỏ field có default | Required fields trong `tools.yaml` |

### B6. Reflection

- `system_prompt.md` phù hợp cho luật hành vi và boundary: không bịa identifier,
  hỏi lại khi thiếu dữ liệu, không tự xác nhận side effect.
- `tools.yaml` phù hợp cho contract từng lời gọi: field nào phải hiện diện và
  cách ánh xạ `topic/timeframe/response_type`.
- R03 cho thấy một run đơn có thể dao động: run v0 gốc fail nhưng các run sau
  không tái hiện. Không nên tuyên bố sửa được lỗi này nếu không có phép thử lặp.
- Routing PASS không đồng nghĩa execution PASS: G07 thiếu Telegram credentials,
  nên cần cấu hình env và chạy live chat riêng nếu muốn chứng minh gửi thật.
- V2 chứng minh aggregate accuracy không phải metric duy nhất: base vẫn 95% nhưng
  targeted confirmation subset tăng từ 0% lên 100%.
- Bước tiếp theo nên chạy lặp nhiều lần hoặc bổ sung paraphrase holdout để đo độ
  ổn định, thay vì tiếp tục tối ưu trên bộ đã đạt trần.
