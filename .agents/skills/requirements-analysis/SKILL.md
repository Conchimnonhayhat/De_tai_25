---
name: requirements-analysis
description: Analyze software requirements and transform natural-language requirements into structured functional requirements, non-functional requirements, user stories, acceptance criteria, and traceability information.
---

# Requirements Analysis Skill

## Objective
Analyze software requirements systematically and produce a structured specification suitable for subsequent architecture, database, implementation, and testing activities.

## Inputs
Read the following project artifacts when available:
- Detai25.1.docx (URD gốc), docs/customer-requirement.md và de_tai_25.md
- business requirements
- existing requirements documentation
- project constraints

## Process
### 1. Identify stakeholders
Identify Admin, workshop manager, team leader and employee as URD actors and stakeholders.

### 2. Identify actors
Identify the four URD actors: Admin, manager, team leader and employee; record any remaining permission ambiguity.

### 3. Identify functional requirements
Convert explicit business needs into functional requirements.
Use IDs: FR-01, FR-02, ..., FR-17.

### 4. Identify non-functional requirements
Identify requirements related to performance, security, reliability, usability, maintainability, scalability.
Use IDs: NFR-01, NFR-02, ..., NFR-11.

### 5. Identify business rules
List business rules explicitly stated by the requirements (BR-01 to BR-09). Do not invent business rules.

### 6. Identify assumptions
Separate assumptions from actual requirements.

### 7. Identify ambiguities
Identify requirements that are ambiguous, incomplete, contradictory, not testable.

### 8. Create user stories
Use: As a <role>, I want <capability>, so that <benefit>.

### 9. Create acceptance criteria
Each important user story must have testable acceptance criteria (Given/When/Then).

### 10. Traceability
Every user story must be traceable to one or more requirements.

## Rules
- Do not write source code.
- Do not design the database.
- Do not design the architecture.
- Do not invent undocumented business rules.
- Clearly distinguish requirements from assumptions.
- Clearly identify missing information.

## Outputs
Create or update:
- docs/requirements.md
- docs/user-stories.md
- docs/acceptance-criteria.md
- docs/requirements-issues.md
- docs/use-cases.md

## Verification
Before completing the task verify:
- all functional requirements have IDs (FR-01 to FR-17);
- all non-functional requirements have IDs (NFR-01 to NFR-11);
- user stories trace to requirements;
- acceptance criteria are testable;
- ambiguities are explicitly documented.
