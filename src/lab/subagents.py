"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "explorer",
            "description": (
                "Use proactively to inspect workspace files, read task specifications, READMEs, "
                "docstrings, schemas, and sample input/output data. Reports objective findings without modifying files."
            ),
            "system_prompt": (
                "You are an exploration subagent. Inspect the workspace, read specifications, data files, and logs, "
                "and return a clear, structured summary of what exists and any rules or constraints found. "
                "Do not modify or create any files."
            ),
        },
        {
            "name": "implementer",
            "description": (
                "Use to make focused code changes, clean data files, process log records, or run tests and helper scripts. "
                "Reports what was changed and the test/script execution outcomes."
            ),
            "system_prompt": (
                "You are an implementation subagent. Make code modifications, clean tabular data, parse logs, or run "
                "scripts according to the exact instructions and rules given to you. Run tests via the shell to verify, "
                "and report exactly what you changed and test results."
            ),
        },
        {
            "name": "reviewer",
            "description": (
                "Use to independently verify the solution, check outputs against all prompt requirements and edge cases, "
                "and validate file contents and formatting before reporting completion."
            ),
            "system_prompt": (
                "You are a review subagent. Independently inspect the solution, verify output files exist and meet all "
                "schema and convention requirements, check for edge cases, and report any discrepancies or confirmation "
                "without modifying files."
            ),
        },
    ]
