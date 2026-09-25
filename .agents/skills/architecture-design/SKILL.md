---
name: architecture-design
description: Design software architecture from approved requirements while preserving traceability and documenting architectural decisions.
---

# Architecture Design Skill

## Objective
Transform approved software requirements into a coherent software architecture.

## Inputs
Read:
- docs/requirements.md
- docs/user-stories.md
- docs/acceptance-criteria.md
Only use approved requirements.

## Process
1. Identify architectural style.
2. Identify major components.
3. Define responsibility of each component.
4. Define dependencies.
5. Define communication between components.
6. Define data flow.
7. Identify external systems.
8. Identify security boundaries.
9. Document architectural decisions (ADRs).
10. Check requirements-to-architecture traceability.

## Rules
- Do not implement source code.
- Do not modify approved requirements.
- Do not introduce unnecessary technologies.
- Every major architectural decision must have a rationale.

## Outputs
Create:
- docs/architecture.md
- docs/architecture-decisions.md
- docs/diagrams/architecture.puml
- docs/diagrams/production-activity.puml
- docs/diagrams/progress-sequence.puml
- docs/diagrams/domain-class.puml
- docs/diagram-review.md

## Verification
Verify that every major functional requirement is supported by at least one architectural component.
Phối hợp diagram-design và uml-diagrams để tạo source/ảnh kiến trúc, Activity, Sequence và Class; giữ truy vết về FR đã duyệt.
