---
name: database-design
description: Design normalized relational schemas and data dictionaries adhering to workshop domain requirements and constraints.
---

# Database Design Skill

## Objective
Design a fully normalized (3NF) relational database schema for the small manufacturing workshop management system based on the 11 entities in the approved URD.

## Inputs
Read:
- docs/requirements.md
- docs/architecture.md
- docs/requirements-issues.md

## Process
1. Model the 11 entities from URD Detai25.1.docx:
   - TaiKhoan
   - SanPham
   - NguyenLieu
   - DinhMucNguyenLieu
   - DonSanXuat
   - CongDoan
   - KeHoachSanXuat
   - PhanCong
   - TienDoCongDoan
   - SuDungNguyenLieu
   - LoiSanXuat
2. Define Primary Keys (PK) and Foreign Keys (FK) with appropriate cascade rules.
3. Address the MaDon gap in TienDoCongDoan and PhanCong as approved in Human Gate 1.
4. Establish column constraints (NOT NULL, UNIQUE, CHECK > 0, DEFAULT).
5. Add performance indexes for frequent lookups (status, foreign keys, order progress).
6. Create Data Dictionary documenting each table, field, datatype, description.
7. Generate valid SQL schema (`database/schema.sql`).
8. Generate ERD source (`docs/diagrams/erd.puml`).

## Rules
- Do not add undocumented tables outside the 11 URD entities without approval.
- Ensure SoLuong values are non-negative.
- Passwords must accommodate secure hash lengths (VARCHAR(255)).
- Maintain strict referential integrity.

## Outputs
- docs/database-design.md
- docs/data-dictionary.md
- database/schema.sql
- docs/diagrams/erd.puml

## Verification
- Verify 11 tables match URD.
- Verify no orphan foreign keys.
- Verify schema matches ERD diagram.
