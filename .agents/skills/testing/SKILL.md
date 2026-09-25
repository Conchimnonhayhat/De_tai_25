---
name: testing
description: Design, implement and execute automated unit and integration tests to verify requirements and business rules.
---

# Testing Skill

## Objective
Establish automated test suites covering functional requirements, business rules (BR-01 to BR-09), edge cases, and security boundaries.

## Process
1. Test Scenarios: Identify test scenarios from docs/acceptance-criteria.md and docs/requirements.md.
2. Test Cases: Define explicit input, expected output, and edge conditions.
3. Automated Tests: Implement pytest tests covering:
   - Authentication & Role-based Access Control (RBAC).
   - Order creation & feasibility checks.
   - Sequential progress constraints (subsequent op <= preceding op).
   - Defect logging and product rejection counting.
   - Material consumption and stock deduction atomicity.
   - Defect rate formula (BR-06) including zero-output handling.
   - Edge cases: Negative quantities, zero quantities, unauthorized API access.
4. Execution: Run `pytest tests/ -v`.
5. Capture real command output, duration, and test counts.
6. Record results into `docs/test-report.md`.

## Rules
- Never mark a test as PASS without executing it in the shell.
- Do not modify test assertions merely to make failing code pass.
- Maintain independent test state using clean fixtures.
