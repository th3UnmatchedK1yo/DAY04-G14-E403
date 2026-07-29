# Version artifact map

Các version được tạo tuần tự từ lỗi của version ngay trước:

| Version | System prompt | Tool schema |
|---|---|---|
| v0 baseline snapshot | `v0_system_prompt.md` | `v0_tools.yaml` |
| v1 | `v1_system_prompt.md` | `v0_tools.yaml` |
| v2 | `v2_system_prompt.md` | `v0_tools.yaml` |
| v3 | `v2_system_prompt.md` | `v3_tools.yaml` |

Artifact mặc định ở thư mục cha (`system_prompt.md`, `tools.yaml`) là trạng thái
v3 để `chat.py` và `run_eval.py` có thể dùng trực tiếp.

Snapshot v0 có cùng nội dung semantic với artifact của run v0 gốc. Hash byte của
snapshot khác run gốc vì snapshot dùng LF còn file Windows ban đầu dùng CRLF;
YAML/prompt được parse thành cùng nội dung.
