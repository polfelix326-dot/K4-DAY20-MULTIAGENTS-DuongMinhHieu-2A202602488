---
name: enforce-schema-and-format-rules
description: Use this skill when generating JSON, CSV, or structured output files to ensure all schema versions, metadata blocks, type formats (e.g. integer cents for money, UTC ISO-8601 timestamps), and naming conventions match specifications precisely.
---
## Schema & Output Formatting Checklist
1. **Review All Rules First**: Before writing output files (`json`, `csv`, etc.), list all formatting rules from the prompt/instructions.
2. **Naming Conventions**: Check if keys, enum values, or identifiers require specific transformations (e.g., replacing hyphens with underscores, lower-casing, or canonical capitalization).
3. **Data Types & Units**:
   - Ensure monetary values are stored in the requested format (e.g., integer cents instead of floats).
   - Ensure timestamps adhere strictly to the requested format (e.g., `YYYY-MM-DDTHH:MM:SSZ` in UTC).
4. **Metadata & Schema Headers**: Include all required metadata blocks (e.g., row counts, source filenames, schema version integers) at the top level of output objects.
5. **Validation**: Write a small script to validate the output file against every rule before completing the task.
