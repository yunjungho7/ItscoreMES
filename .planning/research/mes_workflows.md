# MES Workflows: Industry Standards & Stabilization

**Focus:** Logistics (Inventory, Purchase, Shipment) & Production (Workorders, Lots, Daily Reports)
**Project Context:** Brownfield stabilization of NEWMES.

## 1. Industry Standards (ISA-95 / IEC 62264)

### Logistics Workflows
*   **Inventory Operations:** Must track material definition, lot/serial information, and physical location. Standards require real-time synchronization between the shop floor (MES) and the warehouse/ERP (Level 4).
*   **Purchase (Receipt):** Validation must ensure that incoming materials match the Purchase Order (PO) and that quality checks are performed before the material is "Released" for production.
*   **Shipment:** Final product lots must be validated against sales orders and quality disposition before shipping.

### Production Workflows
*   **Workorders (Detailed Scheduling):** The transition from a Plan to a Workorder must validate resource availability (Machine, Labor, Material).
*   **Lots (Execution tracking):** Every production event (Move, Consume, Produce) must be recorded against a unique Lot ID.
*   **Daily Reports (Data Acquisition):** Aggregated production metrics (Scrap, Downtime, Throughput) must be derived from granular lot-level events to ensure accuracy.

## 2. Common Data Integrity Issues in Brownfield MES

| Issue | Description | Mitigation Strategy |
|-------|-------------|---------------------|
| **Referential Decay** | Links between Production and Master Data (Parts, Lines) are broken. | Implement service-layer existence checks before every write operation. |
| **Shadow Logic** | Critical business rules are hidden in legacy SQL triggers or frontend code. | Centralize logic in Python Services; document SQL "magic". |
| **Missing Handshakes** | Communication between Logistics and Production is missing validations. | Enforce that a Lot cannot be "Started" if its raw material isn't "Consumed" in Inventory. |
| **Audit Gaps** | Changes to stock levels occur without a "Who/When/Why" record. | Implement mandatory History logging for all stock adjustments. |

## 3. Validation Requirements for NEWMES Stabilization

### Logistics Module
1.  **Inventory:**
    - `PARTNO`, `LOC_CD`, `WH_CD` must exist in Master Data.
    - `QTY` must be $\ge 0$ unless explicitly allowed for specific "Virtual" locations.
    - Stock movement must record `OLD_QTY`, `NEW_QTY`, and `USER_ID`.
2.  **Purchase:**
    - Receipts must reference a valid `PO_NO`.
    - Received quantities cannot exceed PO quantity by more than a defined tolerance (e.g., 5%).
3.  **Shipment:**
    - Shipped Lots must have a "RELEASED" or "PASS" quality status.

### Production Module
1.  **Workorders:**
    - Status transitions must be strictly enforced (e.g., Cannot "Complete" if status is "Planned").
    - Expected completion date cannot be earlier than start date.
2.  **Lots:**
    - Every Lot must have a parent `WORKORDNO` and `PARTNO`.
    - Lot creation must generate an entry in the `LOT_HISTORY` table.
3.  **Daily Reports:**
    - Sum of `GOOD_QTY` + `FAIL_QTY` must equal `TOTAL_QTY`.
    - Machine `DOWNTIME` cannot exceed 24 hours in a single daily report.

## 4. Implementation Recommendations

*   **Transactional Integrity:** Use context managers in Python to ensure that if a Lot creation fails, the corresponding History record is not left as an orphan (and vice versa).
*   **ALCOA+ Compliance:** Ensure all `sys_user` references are validated and that timestamps are consistent (DB-generated UTC).
*   **Constraint Hardening:** Move beyond simple API checks by adding `FOREIGN KEY` and `CHECK` constraints to the database schema where possible without breaking the brownfield constraint.

## Sources
- ISA-95 Functional Models (Part 3 & 4)
- GAMP 5: A Risk-Based Approach to Compliant GxP Computerized Systems
- FDA 21 CFR Part 11 (Electronic Records; Electronic Signatures)
