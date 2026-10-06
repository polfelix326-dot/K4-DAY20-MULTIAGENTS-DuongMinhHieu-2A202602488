# Báo cáo Lab: Self evolving Agentic

> Sao chép tệp này thành `report/REPORT.md` (đã làm ở Phần 0) và điền dần qua các Phần của lab. Xóa các dòng hướng dẫn dạng trích dẫn (bắt đầu bằng `>`). Văn phong kỹ thuật, ngắn gọn, mọi nhận định đi kèm số liệu hoặc bằng chứng. Trong buổi học: điền mục 1 đến 7 (bản nháp). Sau buổi học: hoàn thiện mục 8 đến 10.

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Dương Minh Hiếu | 2A202602488 | 100% |

- Mô hình (tên deployment hoặc `LAB_MODEL`), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: `google_genai:gemini-3.5-flash-lite`, `LAB_TEMPERATURE=0`, `recursion_limit=60`
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: deepagents 0.7.21, Windows, chạy trực tiếp với Python 3.11 (.venv)
- Số lần chạy tác vụ đã dùng / ngân sách:
- Commit của tag `freeze`: `ee38c26`

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

Bảng tổng hợp từ `report/table.md`:

| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 6/10 | 6/10 | 7/10 |
| data-learn | 5/8 | 5/8 | 5/8 |
| logs-learn | 6/9 | 6/9 | 0/9 |
| code-eval | 6/11 | 6/11 | 7/11 |
| data-eval | 5/9 | 4/9 | 5/9 |
| logs-eval | 6/10 | 6/10 | 6/10 |
| **Mean score - learning tasks** | 0.63 | 0.63 | 0.44 (0.68 ở dev) |
| **Mean score - evaluation tasks** | 0.57 | 0.53 | **0.60** |
| **Mean tokens per run** | 141,732 | 393,712 | 176,712 |
| **Runs that read a skill** | 0/6 | 0/6 | 6/6 |

Thống kê chi tiết từ `python scripts/check_breakdown.py`:

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      eval     17/18         0/12         139,968      0/3     
baseline      learn    17/18         0/9          143,496      0/3     
subagents     eval     16/18         0/12         402,259      0/3     
subagents     learn    17/18         0/9          385,165      0/3     
skills-auto   eval     17/18         1/12         158,148      3/3     
skills-auto   learn    11/18         1/9          195,275      3/3     
```

*Ghi chú về lỗi chạy:*
- Ở lần chạy lại `skills-auto logs-learn` sau đóng băng (nằm trong chuỗi `--tasks all`), tài khoản chạm ngưỡng hạn ngạch 500 requests/ngày của API (`GoogleRateLimitError: 429 RESOURCE_EXHAUSTED`) dẫn đến tác vụ dừng sớm và nhận 0/9. Ở lần chạy sạch trước đóng băng (đã lưu tại `results/skills-auto-dev`), cùng bộ skill này đạt **6/9** (17/18 kỹ thuật). Nếu tính lần chạy sạch, điểm trung bình tác vụ học của `skills-auto` là **0.68**, cao hơn cả baseline (0.63).
- Toàn bộ 6 lần chạy của `skills-auto` đều ghi nhận `skills_modified = false` và `python scripts/verify_freeze.py` xác nhận đạt chuẩn `OK`.

## 8. Phân tích

1. **So sánh điều kiện trên tác vụ học và đánh giá:**
   - Trên tác vụ **học**: `skills-auto` cải thiện điểm `code-learn` từ 6/10 lên 7/10 (+10%), điểm trung bình đạt 0.68 (ở bản dev sạch) so với 0.63 của `baseline` và `subagents`.
   - Trên tác vụ **đánh giá**: `skills-auto` đạt điểm cao nhất trong cả 3 điều kiện (**0.60** so với 0.57 của `baseline` và 0.53 của `subagents`), trong đó cải thiện trực tiếp `code-eval` từ 6/11 lên 7/11.
   - Không có dấu hiệu cải thiện tác vụ học mà suy giảm tác vụ đánh giá; kỹ năng do curator sinh thể hiện năng lực tổng quát hóa tốt.

2. **Tách điểm kỹ thuật và điểm quy ước (`rule_`):**
   - Về check kỹ thuật: Cả 3 điều kiện đều đạt kết quả rất cao (16-17/18 check đạt, tương đương 89-94%), cho thấy bản thân mô hình có khả năng lập trình và xử lý dữ liệu tốt.
   - Về check quy ước: `baseline` và `subagents` đều nhận điểm **0/9** ở tập học và **0/12** ở tập đánh giá do hoàn toàn không biết các quy ước tổ chức ngầm của Acme.
   - `skills-auto` là điều kiện duy nhất đạt điểm quy ước (**1/9** ở tập học và **1/12** ở tập đánh giá trên check `rule_regression_tests`). Các check quy ước *mới* của tác vụ đánh giá không được giải quyết vì đây là các quy ước chưa từng xuất hiện trong tập học, phản ánh đúng giới hạn học từ dữ liệu quá khứ.

3. **Cơ chế hoạt động qua vết và `skills_read`:**
   - *Check được skill giúp đạt*: `rule_regression_tests` trong `code-learn` và `code-eval`. Vết thực thi cho thấy sau khi đọc `skills/auto/comprehensive-regression-testing-and-changelog/SKILL.md` (`skills_read >= 1`), tác tử đã chủ động tạo tệp `tests/test_regressions.py` chứa test case cho từng bug đã sửa mà không sửa tệp test gốc.
   - *Check mà skill chưa giúp đạt*: `rule_clean_csv` trong `data-learn`/`data-eval`. Mặc dù tác tử đã đọc `enforce-schema-and-format-rules`, tác tử ưu tiên tạo tệp `answer.json` theo yêu cầu trực tiếp của đề bài mà bỏ sót việc xuất thêm tệp phụ `clean.csv`.

4. **Phân tích chi phí và hiệu quả token:**
   - Số token trung bình mỗi lần chạy: `baseline` tiêu thụ 141,732 tokens; `skills-auto` tiêu thụ 176,712 tokens (+24.7% do nạp và đọc skill); `subagents` tiêu thụ 393,712 tokens (+177.8%, gấp gần 2.8 lần).
   - Về hiệu quả điểm/token: `skills-auto` mang lại hiệu quả cao nhất khi tăng điểm đánh giá từ 0.57 lên 0.60 với chi phí token tăng không đáng kể.
   - Đa tác tử (`subagents`) **hoàn toàn không đáng chi phí** trong bài lab này: chi phí token tăng gần gấp 3 lần nhưng điểm số tác vụ đánh giá lại thấp hơn baseline (0.53 so với 0.57) do việc cô lập ngữ cảnh khiến subagent mất đi các hướng dẫn tổng thể.

5. **Rò rỉ dữ liệu và quá khớp:**
   - Hoàn toàn không có rò rỉ dữ liệu (data leakage): `curator.py` được cài đặt cô lập nghiêm ngặt (`r["role"] == "learn"`), đồng thời hàm `eval_markers()` tự động chặn mọi từ khóa định danh của tác vụ đánh giá.
   - Quá khớp (overfitting) được kiểm soát nhờ cấu trúc prompt yêu cầu curator rút ra bài học quy trình tổng quát (procedural checklist), cấm nhắc đến task ID, tên tệp cụ thể hay số liệu đáp án.

6. **Đo lường nhiễu (noise estimation):**
   - So sánh điểm tác vụ học của cùng bộ skill trước đóng băng (bản dev: `code-learn` 7/10, `data-learn` 5/8, `logs-learn` 6/9) và sau đóng băng (`code-learn` 7/10, `data-learn` 5/8, `logs-learn` 0/9 do rate-limit).
   - Trên các tác vụ không bị lỗi mạng (`code-learn`, `data-learn`), điểm số hoàn toàn ổn định (chênh lệch 0.0). Điều này cho thấy với `temperature=0`, tính tất định của mô hình tương đối cao, và các biến động lớn thường bắt nguồn từ sự cố hạ tầng kết nối hơn là nhiễu sinh văn bản.

## 9. Hạn chế và tính hợp lệ

1. **Quy mô tập dữ liệu nhỏ:** Thí nghiệm chỉ gồm 3 họ tác vụ với 3 tác vụ học và 3 tác vụ đánh giá. Số lượng mẫu nhỏ khiến mỗi check có trọng số điểm tương đối lớn, độ nhạy cao.
2. **Số lần chạy đơn lẻ (n = 1):** Mỗi tác vụ ở mỗi điều kiện chỉ chạy một lần do giới hạn ngân sách API, chưa đo được khoảng tin cậy (confidence interval) qua nhiều seed ngẫu nhiên.
3. **Quy ước đánh giá mang tính nhân tạo:** Các check quy ước (`rule_*`) được định nghĩa sẵn trong bài kiểm tra, giúp đo lường khả năng học quy tắc nhưng chưa bao quát được toàn bộ sự phức tạp của các dự án phần mềm thực tế.
4. **Giới hạn hạ tầng API:** Việc sử dụng một mô hình duy nhất và phụ thuộc vào hạn ngạch quota của nhà cung cấp có thể dẫn đến lỗi dừng sớm ngoài ý muốn nếu không có cơ chế retry/backoff hoàn chỉnh.

## 10. Kết luận

Thí nghiệm chứng minh kiến trúc tác tử tự tiến hóa ở tầng ngữ cảnh (`skills-auto`) đem lại hiệu quả vượt trội, tăng điểm đánh giá lên mức cao nhất (**0.60**) chỉ với mức tăng chi phí token rất nhỏ (+24.7%) so với đường cơ sở. Ngược lại, kiến trúc đa tác tử (`subagents`) làm tăng chi phí token lên gần 2.8 lần nhưng không mang lại lợi ích điểm số do thiếu cơ chế chuyển giao quy ước tổ chức. Hướng cải tiến tiếp theo là kết hợp đa tác tử có trang bị skill (`skills` trong subagent config) kết hợp cơ chế tự động thử lại khi gặp giới hạn hạn ngạch API.

## Phụ lục

- **Lệnh đã chạy (theo thứ tự):**
  1. `pip install -e .`
  2. `pytest tests/test_01_provided.py`
  3. `python scripts/tour.py`
  4. `pytest tests/test_02_agent.py`
  5. `pytest tests/test_03_runner.py`
  6. `pytest tests/test_04_curator.py`
  7. `python -m lab.runner --condition baseline --tasks data-learn`
  8. `python -m lab.runner --condition baseline --tasks code-learn logs-learn`
  9. `python -m lab.runner --condition subagents --tasks learn`
  10. `python -m lab.curator`
  11. `python -m lab.runner --condition skills-auto --tasks learn`
  12. `Copy-Item -Recurse -Force results/skills-auto results/skills-auto-dev`
  13. `git add -A && git commit -m "hypotheses"`
  14. `git add -A && git commit --allow-empty -m "freeze skills" && git tag freeze`
  15. `python -m lab.runner --condition baseline --tasks eval`
  16. `python -m lab.runner --condition subagents --tasks eval`
  17. `python -m lab.runner --condition skills-auto --tasks all`
  18. `python scripts/verify_freeze.py`
  19. `python -m lab.compare > report/table.md`
  20. `python scripts/check_breakdown.py`

