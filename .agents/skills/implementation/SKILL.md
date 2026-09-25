---
name: implementation
description: Implement robust, maintainable and secure software components following approved specifications and architecture.
---

# Implementation Skill

## Objective
Implement system components in Python Flask and relational database adhering to approved requirements and architecture design.

## Process
1. Read Specification: docs/requirements.md, docs/acceptance-criteria.md.
2. Understand Architecture: docs/architecture.md, docs/architecture-decisions.md.
3. Understand Database: docs/database-design.md, database/schema.sql.
4. Implement:
   - Database connection & transactions.
   - Domain models & Data access objects (DAO).
   - Business service layer with validation logic.
   - Controller & Routes with RBAC guards.
   - User interfaces with clean HTML/CSS/JS.
5. Run Linter & Syntax validation.
6. Run Tests: pytest tests/.
7. Review Diff & Report changes.

## Rules
- Do not bypass authentication or role checks.
- Always use parameterized SQL queries (no string formatting/concatenation).
- Enforce transactional integrity when modifying multiple entities.
- Validate inputs at backend (positive quantities, date formats).
- Escape output in HTML templates to prevent XSS.
- Do not hardcode secrets or API keys.
- If specification is ambiguous or insufficient, stop and report rather than guess.

## Outputs
- Source files in models/, routes/, services/, templates/, static/, app.py.
- Verification evidence via tests.
