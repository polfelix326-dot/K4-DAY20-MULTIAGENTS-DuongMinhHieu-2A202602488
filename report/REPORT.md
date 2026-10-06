# Báo cáo Lab: Self evolving Agentic

> Sao chép tệp này thành `report/REPORT.md` (đã làm ở Phần 0) và điền dần qua các Phần của lab. Xóa các dòng hướng dẫn dạng trích dẫn (bắt đầu bằng `>`). Văn phong kỹ thuật, ngắn gọn, mọi nhận định đi kèm số liệu hoặc bằng chứng. Trong buổi học: điền mục 1 đến 7 (bản nháp). Sau buổi học: hoàn thiện mục 8 đến 10.

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Dương Minh Hiếu | 2A202602488 | 100% |

- Mô hình (tên deployment hoặc `LAB_MODEL`), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: `google_genai:gemini-3.5-flash-lite`, `LAB_TEMPERATURE=0`, `recursion_limit=60`
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: deepagents 0.7.21, Windows, chạy trực tiếp với Python 3.11 (.venv)
- Số lần chạy tác vụ đã dùng / ngân sách:
- Commit của tag `freeze`:

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

- H1 (subagents so với baseline): `subagents` sẽ có điểm số tương đương hoặc chỉ tăng nhẹ so với `baseline` trên tác vụ đánh giá (dự đoán dao động trong khoảng ±5%), nhưng sẽ tiêu tốn lượng token gấp 2 đến 3 lần. Căn cứ: Nghiên cứu của Anthropic về multi-agent cho thấy kiến trúc đa tác tử tốn chi phí rất lớn do tái lặp context; ngoài ra các subagent độc lập cũng không nắm được các quy ước ẩn của tổ chức (`rule_*`) nên không thể giải quyết nhóm lỗi E nếu không có skill.
- H2 (skills-auto so với baseline): `skills-auto` sẽ đạt điểm cao hơn `baseline` trên cả tác vụ học và tác vụ đánh giá đối với các quy ước chung được chuyển giao (ví dụ định dạng tiền tệ cents, timezone UTC, regression testing), nhưng mức cải thiện trên tác vụ đánh giá sẽ thấp hơn tác vụ học (hiện tượng overfitting / transfer gap ghi nhận trong SkillEvolBench). Các quy ước hoàn toàn mới xuất hiện ở tác vụ đánh giá sẽ không được phòng ngừa bởi skill cũ.
- H3 (tác vụ học so với tác vụ đánh giá): Điểm trung bình của tất cả các điều kiện trên tác vụ đánh giá sẽ thấp hơn trên tác vụ học. Căn cứ: Tác vụ đánh giá sử dụng dữ liệu mới và bổ sung thêm các quy ước tổ chức mới mà tác tử chưa từng gặp trong tác vụ học, dẫn đến suy giảm độ chính xác tổng thể.

## 3. Làm quen Deep Agents (Phần 0.3)

1. Tác tử mặc định có 9 công cụ: `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute`, `task`. Trong đó, công cụ cho phép chạy lệnh shell là `execute`.
2. Mô tả của công cụ `task` về subagent `general-purpose`: Là tác tử đa năng để nghiên cứu các câu hỏi phức tạp, tìm kiếm tệp/nội dung và thực hiện các tác vụ nhiều bước ("General-purpose agent for researching complex questions, searching for files and content, and executing multi-step tasks..."). Về ngữ cảnh: mỗi lần gọi là phi trạng thái theo mặc định (stateless by default), subagent chỉ nhìn thấy nội dung trong câu lệnh/prompt mà tác tử chính gửi trực tiếp cho nó và trả về một báo cáo kết quả cuối cùng; nó không tự động thấy lịch sử hội thoại của tác tử chính trừ khi được chỉ định kế thừa.
3. Câu hướng dẫn hành vi từ mô tả của công cụ `task`: "Each invocation is stateless by default: the agent sees only the prompt you give it and returns a single final report. Put full detail in the prompt and state exactly what it should return."
Câu hướng dẫn hành vi từ mô tả của công cụ `execute`: "You MUST avoid using search commands like find and grep. Instead use the grep, glob tools to search. Use read_file rather than cat/head/tail."

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| `code-learn` | `tests_not_modified` | A | `the original files in tests/ must not be modified (new test files are allowed)` (vết: sửa `tests/test_report.py`) |
| `code-learn` | `rule_type_hints` | E | `RULE: every public function (name not starting with '_') in the package has type annotations on all parameters and on the return value.` |
| `code-learn` | `rule_regression_tests` | E | `RULE: add tests/test_regressions.py with one test function per bug you fixed (at least 3); the file must pass.` |
| `code-learn` | `rule_changelog` | E | `RULE: record each fix in CHANGELOG.md under the heading '## Unreleased' as a bullet '- fix(<function name>): <short description>' (at least 3 bullets).` |
| `data-learn` | `rule_money_in_cents` | E | `RULE: money values in answer.json are integer cents (1606.67 USD is written 160667).` |
| `data-learn` | `rule_meta_block` | E | `RULE: answer.json has an object meta = {"source": <input file name>, "rows_in": <number of data rows>, "rows_used": <number of distinct orders>}.` |
| `data-learn` | `rule_clean_csv` | E | `RULE: write workspace/clean.csv with the header order_id,timestamp_utc,region,amount_cents; one row per distinct order...` |
| `logs-learn` | `rule_service_names` | E | `RULE: service names in the output are lower-case with '-' replaced by '_' (payment-service -> payment_service).` |
| `logs-learn` | `rule_sorted_errors` | E | `RULE: errors is sorted by service, then by timestamp_utc, ascending.` |
| `logs-learn` | `rule_schema_header` | E | `RULE: the top-level object has "schema_version": 2 and "generated_by": "log-triage".` |

**Nhận xét:**
- Nhóm lỗi **E (Vi phạm quy ước tổ chức)** chiếm đa số áp đảo (9/10 check thất bại, tức 90%). Đúng 1 lỗi thuộc nhóm A (`tests_not_modified` do tác tử sửa file test có sẵn thay vì chỉ sửa source code).
- **Bằng chứng phủ định cho các nhóm A đến D:** Theo thống kê từ `scripts/check_breakdown.py`, tác tử đạt tới **17/18 check kỹ thuật (94.4%)**. Điều này chứng minh mô hình xử lý rất tốt các yêu cầu thuật toán, định dạng ngày tháng, tính toán múi giờ, phân tích log và sửa bug. Tác tử không bị thiếu năng lực kỹ thuật mà chỉ thiếu nhận thức về các "quy ước ngầm của tổ chức" (`rule_*`) vốn không được nêu tường minh trong đề bài.
- **Khả năng phòng ngừa bằng Skill:** Hoàn toàn khả thi. Khi curator đọc các phản hồi `RULE:` từ bot đánh giá và tổng hợp thành skill quy trình (Acme conventions checklist), tác tử nạp skill sẽ biết các quy ước này và tuân thủ ngay từ đầu.

## 5. Điều kiện `subagents` (Phần 2.3)

- **Các subagent đã định nghĩa:**
  1. `explorer`: Chuyên đọc và khảo sát cấu trúc workspace, schema, docstring, tệp cấu hình mà không sửa đổi tệp.
  2. `implementer`: Chuyên thực hiện các thay đổi code/data, chạy script dọn dẹp và test shell, báo cáo kết quả.
  3. `reviewer`: Chuyên độc lập kiểm tra kết quả theo yêu cầu đề bài và edge case trước khi nộp.
- **`subagent_calls` ở từng tác vụ và nhận xét:**
  - `code-learn`: 6 lần gọi subagent (tác tử chính gọi `explorer` tìm hiểu bug và `implementer` sửa code, sau đó dùng `reviewer`).
  - `data-learn`: 3 lần gọi subagent (chia việc phân tích và xử lý dữ liệu).
  - `logs-learn`: 13 lần gọi subagent (chia nhỏ việc xử lý các khối log).
  - Nhận xét: Tác tử chính tuân thủ tốt `SUBAGENTS_NOTE`, chủ động phân rã tác vụ và ủy quyền cho các subagent chuyên biệt.
- **Thông tin thiếu hoặc thừa khi giao việc:** Do subagent là stateless và không thừa kế ngữ cảnh luồng chính, tác tử chính phải truyền lại đường dẫn tương đối và mô tả chi tiết. Thỉnh thoảng prompt giao việc còn lặp lại mô tả đề bài đầy đủ, gây tiêu tốn token.
- **Ảnh hưởng đến token và thời gian:**
  - Token tiêu thụ trung bình tăng gấp gần 2.7 lần: **385,165 tokens** ở `subagents` so với **143,496 tokens** ở `baseline`.
  - Thời gian thực thi tăng đáng kể do nhiều lượt gọi LLM lồng nhau.
  - Điểm số không tăng so với `baseline` (đều 17/18 kỹ thuật và 0/9 quy ước) vì subagent cũng chưa được trang bị tri thức về các quy ước tổ chức ẩn (`rule_*`).

## 6. Self-evolving: skill do curator sinh (Phần 3)

- **Số lần chạy curator, số skill bị xóa và lý do:** Chạy curator 1 lần thành công; sinh ra 2 skill hợp lệ vào `skills/auto/`; 0 skill bị xóa vì cả 2 skill đều đạt chuẩn an toàn, định dạng hợp lệ và có tính khái quát cao.

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `enforce-schema-and-format-rules` | **Tổng quát**: Nêu nguyên tắc chung về kiểm tra quy định format trước khi ghi file, chuẩn hóa naming convention, đổi tiền tệ sang cents, timestamp UTC ISO-8601, gắn header metadata. Không chứa ID hay số liệu riêng của tác vụ học. | **Đúng**: Cung cấp checklist 5 bước rất rõ ràng, không có chỉ dẫn sai hoặc gây hại. | 13 dòng (ngắn gọn, dưới giới hạn 40 dòng). `description` nêu rõ khi nào dùng (khi tạo file JSON/CSV có cấu trúc). `skills_read` = 0 (tác tử giải quyết data-learn/logs-learn bằng context có sẵn). |
| `comprehensive-regression-testing-and-changelog` | **Tổng quát**: Nêu quy tắc sửa mã nguồn chuyên nghiệp: không sửa test gốc trong `tests/`, bổ sung type hint cho hàm public, thêm regression test và ghi changelog. Không nêu tên hàm hay file cụ thể của inventory. | **Đúng**: Rất chính xác theo chuẩn kỹ thuật phần mềm và quy ước đề bài. | 10 dòng. `description` nêu rõ tình huống kích hoạt (khi sửa bug/modify package). `skills_read` = 1 (tác tử đã đọc và áp dụng trong `code-learn`, giúp vượt qua check `rule_regression_tests`). |

## 7. Kết quả so sánh (Phần 4.3, 4.4)

> Dán nội dung `report/table.md` và kết quả `python scripts/check_breakdown.py`. Nêu các lần chạy có `error` hoặc `skills_modified = true` (nếu có) và cách xử lý.

```text
(dán bảng ở đây)
```

## 8. Phân tích

> Trả lời từng câu bằng số liệu từ mục 7 và bằng chứng từ vết. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.

1. So với `baseline`, điều kiện nào cải thiện điểm tác vụ **học**? Điều kiện nào cải thiện điểm tác vụ **đánh giá**? Có điều kiện nào cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá? Nếu có, đó là dấu hiệu gì?
2. Tách điểm thành check kỹ thuật và check quy ước (`rule_`). Skill do curator sinh giúp nhóm check nào? Check quy ước **mới** của tác vụ đánh giá có được skill giúp không, và vì sao?
3. Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp (skill chưa được đọc, đọc nhưng không làm theo, skill thiếu hoặc sai).
4. Chi phí: so sánh số token trung bình giữa các điều kiện. Điều kiện nào có hiệu quả tốt nhất theo điểm trên mỗi token? Đa tác tử có đáng chi phí trong thí nghiệm này không?
5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Nhóm đã phòng tránh như thế nào?
6. Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?

## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1.
2.
3.

## 10. Kết luận

> Tối đa 5 câu. Chỉ khẳng định điều số liệu hỗ trợ. Nêu một đề xuất cải tiến tiếp theo.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
- Thử thách mở rộng (nếu có): hướng chọn, kết quả, nhận xét.
- Ghi chú khác:
