# PFMES 트랜잭션 데이터 삭제 쿼리

> ⚠️ **주의**: 이 쿼리는 기준정보(마스터) 테이블을 **제외**하고, 운영 데이터(트랜잭션)만 삭제합니다.
> 실행 전 반드시 **백업**을 수행하시기 바랍니다.

---

## 보존되는 기준정보 테이블 (삭제 대상 아님)

| 구분 | 테이블명 | 설명 |
|------|----------|------|
| 기준정보 | TBL_COM_PLANT | 사업장 |
| 기준정보 | TBL_COM_FACTORY | 공장 |
| 기준정보 | TBL_COM_LINE | 라인 |
| 기준정보 | TBL_COM_PROCESS | 공정 |
| 기준정보 | TBL_COM_PROCESS_USER | 공정별 사용자 |
| 기준정보 | TBL_COM_WAREHOUSE | 창고 |
| 기준정보 | TBL_COM_LOCATION | 로케이션 |
| 기준정보 | TBL_COM_GOODS | 품목 |
| 기준정보 | TBL_COM_BOM | BOM |
| 기준정보 | TBL_COM_COMPANY | 거래처 |
| 기준정보 | TBL_COM_DEPT | 부서 |
| 기준정보 | TBL_COM_FAILCODE | 불량코드 |
| 기준정보 | TBL_COM_CODE | 공통코드 |
| 검사기준 | TBL_INSP_ITEM | 검사항목 |
| 검사기준 | TBL_INSP_STANDARD | 검사기준 |
| 검사기준 | TBL_INSP_STANDARD_ITEM | 검사기준 항목 |
| 시스템 | TBL_COM_MEMBERS | 사용자 |
| 시스템 | TBL_COM_MENU | 메뉴 |

---

## 삭제 대상 트랜잭션 테이블

| 구분 | 테이블명 | 설명 |
|------|----------|------|
| 생산 | TBL_PROD_FAILQTY_HISTORY | 불량 이력 |
| 생산 | TBL_PROD_FAILQTY | 불량수량 |
| 생산 | TBL_PROD_STOCK_HISTORY | 재고 이력 |
| 생산 | TBL_PROD_STOCK | 재고 |
| 생산 | TBL_PROD_LOTHISTORY | LOT 이력 |
| 생산 | TBL_PROD_LOTSTATE | LOT 상태 |
| 생산 | TBL_PROD_PRODINFO | 생산실적 |
| 생산 | TBL_PROD_PRODUCEPLAN | 생산계획 |
| 생산 | TBL_PROD_WORKORDER | 작업지시 |
| 물류 | TBL_INOUT_SHIPMENT_INDICATION_DTL | 출하지시 상세 |
| 물류 | TBL_INOUT_SHIPMENT_INDICATION | 출하지시 |
| 물류 | TBL_INOUT_WAREHOUSE_DETAIL | 입고 상세 |
| 물류 | TBL_INOUT_WAREHOUSE | 입고 |
| 물류 | TBL_INOUT_PURCHASE_ORDER_DETAIL | 발주 상세 |
| 물류 | TBL_INOUT_PURCHASE_ORDER | 발주 |
| 물류 | TBL_INOUT_ORDER_DETAIL | 수주 상세 |
| 물류 | TBL_INOUT_ORDERS | 수주 |
| 검사 | TBL_PQC_TESTSCORE | 검사성적 |

---

## 삭제 쿼리

> FK(외래키) 참조 순서를 고려하여 **자식 테이블 → 부모 테이블** 순서로 삭제합니다.
> 트랜잭션 안에서 실행하여 문제 발생 시 롤백할 수 있도록 합니다.

```sql
-- ============================================================
-- PFMES 트랜잭션 데이터 전체 삭제 스크립트
-- 기준정보(마스터) 테이블은 보존됩니다.
-- ============================================================
-- 실행 전 백업 권장
-- ============================================================

BEGIN TRANSACTION;

BEGIN TRY

-- ──────────────────────────────────────────────
-- 1. 검사 (Inspection)
-- ──────────────────────────────────────────────
PRINT '▶ 검사성적 삭제...'
DELETE FROM TBL_PQC_TESTSCORE;

-- ──────────────────────────────────────────────
-- 2. 생산 - 불량 (Production - Defect)
-- ──────────────────────────────────────────────
PRINT '▶ 불량 이력 삭제...'
DELETE FROM TBL_PROD_FAILQTY_HISTORY;

PRINT '▶ 불량수량 삭제...'
DELETE FROM TBL_PROD_FAILQTY;

-- ──────────────────────────────────────────────
-- 3. 생산 - 재고 (Production - Stock)
-- ──────────────────────────────────────────────
PRINT '▶ 재고 이력 삭제...'
DELETE FROM TBL_PROD_STOCK_HISTORY;

PRINT '▶ 재고 삭제...'
DELETE FROM TBL_PROD_STOCK;

-- ──────────────────────────────────────────────
-- 4. 생산 - LOT (Production - LOT)
-- ──────────────────────────────────────────────
PRINT '▶ LOT 이력 삭제...'
DELETE FROM TBL_PROD_LOTHISTORY;

PRINT '▶ LOT 상태 삭제...'
DELETE FROM TBL_PROD_LOTSTATE;

-- ──────────────────────────────────────────────
-- 5. 생산 - 실적/계획/작업지시
-- ──────────────────────────────────────────────
PRINT '▶ 생산실적 삭제...'
DELETE FROM TBL_PROD_PRODINFO;

PRINT '▶ 생산계획 삭제...'
DELETE FROM TBL_PROD_PRODUCEPLAN;

PRINT '▶ 작업지시 삭제...'
DELETE FROM TBL_PROD_WORKORDER;

-- ──────────────────────────────────────────────
-- 6. 물류 - 출하 (Logistics - Shipment)
-- ──────────────────────────────────────────────
PRINT '▶ 출하지시 상세 삭제...'
DELETE FROM TBL_INOUT_SHIPMENT_INDICATION_DTL;

PRINT '▶ 출하지시 삭제...'
DELETE FROM TBL_INOUT_SHIPMENT_INDICATION;

-- ──────────────────────────────────────────────
-- 7. 물류 - 입고 (Logistics - Receive)
-- ──────────────────────────────────────────────
PRINT '▶ 입고 상세 삭제...'
DELETE FROM TBL_INOUT_WAREHOUSE_DETAIL;

PRINT '▶ 입고 삭제...'
DELETE FROM TBL_INOUT_WAREHOUSE;

-- ──────────────────────────────────────────────
-- 8. 물류 - 발주 (Logistics - Purchase Order)
-- ──────────────────────────────────────────────
PRINT '▶ 발주 상세 삭제...'
DELETE FROM TBL_INOUT_PURCHASE_ORDER_DETAIL;

PRINT '▶ 발주 삭제...'
DELETE FROM TBL_INOUT_PURCHASE_ORDER;

-- ──────────────────────────────────────────────
-- 9. 물류 - 수주 (Logistics - Sales Order)
-- ──────────────────────────────────────────────
PRINT '▶ 수주 상세 삭제...'
DELETE FROM TBL_INOUT_ORDER_DETAIL;

PRINT '▶ 수주 삭제...'
DELETE FROM TBL_INOUT_ORDERS;

    -- ──────────────────────────────────────────────

    COMMIT TRANSACTION;
    PRINT '✅ 모든 트랜잭션 데이터가 성공적으로 삭제되었습니다.'

END TRY
BEGIN CATCH

    ROLLBACK TRANSACTION;
    PRINT '❌ 오류 발생 - 롤백되었습니다.'
    PRINT ERROR_MESSAGE();

END CATCH;
```

---

## 건수 확인 쿼리 (삭제 전/후 확인용)

```sql
-- 삭제 대상 테이블 건수 확인
SELECT 'TBL_PQC_TESTSCORE' AS TABLE_NAME, COUNT(*) AS CNT FROM TBL_PQC_TESTSCORE
UNION ALL SELECT 'TBL_PROD_FAILQTY_HISTORY', COUNT(*) FROM TBL_PROD_FAILQTY_HISTORY
UNION ALL SELECT 'TBL_PROD_FAILQTY', COUNT(*) FROM TBL_PROD_FAILQTY
UNION ALL SELECT 'TBL_PROD_STOCK_HISTORY', COUNT(*) FROM TBL_PROD_STOCK_HISTORY
UNION ALL SELECT 'TBL_PROD_STOCK', COUNT(*) FROM TBL_PROD_STOCK
UNION ALL SELECT 'TBL_PROD_LOTHISTORY', COUNT(*) FROM TBL_PROD_LOTHISTORY
UNION ALL SELECT 'TBL_PROD_LOTSTATE', COUNT(*) FROM TBL_PROD_LOTSTATE
UNION ALL SELECT 'TBL_PROD_PRODINFO', COUNT(*) FROM TBL_PROD_PRODINFO
UNION ALL SELECT 'TBL_PROD_PRODUCEPLAN', COUNT(*) FROM TBL_PROD_PRODUCEPLAN
UNION ALL SELECT 'TBL_PROD_WORKORDER', COUNT(*) FROM TBL_PROD_WORKORDER
UNION ALL SELECT 'TBL_INOUT_SHIPMENT_INDICATION_DTL', COUNT(*) FROM TBL_INOUT_SHIPMENT_INDICATION_DTL
UNION ALL SELECT 'TBL_INOUT_SHIPMENT_INDICATION', COUNT(*) FROM TBL_INOUT_SHIPMENT_INDICATION
UNION ALL SELECT 'TBL_INOUT_WAREHOUSE_DETAIL', COUNT(*) FROM TBL_INOUT_WAREHOUSE_DETAIL
UNION ALL SELECT 'TBL_INOUT_WAREHOUSE', COUNT(*) FROM TBL_INOUT_WAREHOUSE
UNION ALL SELECT 'TBL_INOUT_PURCHASE_ORDER_DETAIL', COUNT(*) FROM TBL_INOUT_PURCHASE_ORDER_DETAIL
UNION ALL SELECT 'TBL_INOUT_PURCHASE_ORDER', COUNT(*) FROM TBL_INOUT_PURCHASE_ORDER
UNION ALL SELECT 'TBL_INOUT_ORDER_DETAIL', COUNT(*) FROM TBL_INOUT_ORDER_DETAIL
UNION ALL SELECT 'TBL_INOUT_ORDERS', COUNT(*) FROM TBL_INOUT_ORDERS
ORDER BY TABLE_NAME;
```
