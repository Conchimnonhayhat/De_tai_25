---
name: production-data-retrieval
description: Retrieve verified, authorized production snapshot data using parameterized SQL for AI analysis.
---

# Production Data Retrieval Skill

## Objective
Extract accurate, bounded database snapshots strictly adhering to user permissions and structured intent specifications.

## Process
1. Build parameterized SQL queries according to `task_type` and `order_ids`.
2. Apply authorization filters (Tổ trưởng only views assigned team orders; Quản lý views workshop scope).
3. Retrieve orders, operations, progress, defects, and raw material stocks.
4. Flag missing or contradictory records (`missing_data`, `data_issues`).
5. Enforce deterministic sorting (e.g. `ORDER BY HanGiao ASC`).

## Rules
- Never use SQL string concatenation.
- Never dump entire tables unnecessarily.
- Maintain source record identifiers (`source_ids`) for complete traceability.
