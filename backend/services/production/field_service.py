"""현장 생산관리 서비스"""
from db.xml_mapper import XMLMapper
from db.connection import get_db_connection
import math
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class FieldService:
    def __init__(self):
        self.mapper = XMLMapper(os.path.join(BASE_DIR, 'sql/production/field.xml'))

    def get_workorders(self, start_date=None, end_date=None, shift=None,
                       ord_state=None, line_cd=None, process_cd=None,
                       workord_no=None, search=None, include_done=False, page=1, size=50):
        params = {}
        if start_date: params['start_date'] = start_date
        if end_date: params['end_date'] = end_date
        if shift: params['shift'] = shift
        if ord_state: params['ord_state'] = ord_state
        if line_cd: params['line_cd'] = line_cd
        if process_cd: params['process_cd'] = process_cd
        if workord_no: params['workord_no'] = f'%{workord_no}%'
        if search: params['search'] = f'%{search}%'
        params['include_done'] = 'true' if include_done else 'false'

        conn = get_db_connection()
        cursor = conn.cursor()

        # Count
        q = self.mapper.get_query('countFieldWorkorders', params)
        values = tuple(params.get(name) for name in q['params'])
        cursor.execute(q['query'], values)
        total = cursor.fetchone()[0]

        # Select
        params['offset'] = (page - 1) * size
        params['limit'] = size
        q = self.mapper.get_query('selectFieldWorkorders', params)
        values = tuple(params.get(name) for name in q['params'])
        cursor.execute(q['query'], values)
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()

        return {
            "data": rows,
            "total": total,
            "page": page,
            "totalPages": math.ceil(total / size) if total else 0
        }

    def get_summary(self, workordno):
        params = {'WORKORDNO': workordno}
        q = self.mapper.get_query('selectProductionSummary', params)
        values = tuple(params.get(name) for name in q['params'])
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(q['query'], values)
        columns = [col[0] for col in cursor.description]
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(zip(columns, row))
        return {
            'ORD_QTY': 0, 'TOT_PROD_QTY': 0, 'TOT_GOOD_QTY': 0,
            'TOT_FAIL_QTY': 0, 'PROD_QTY': 0, 'GOOD_QTY': 0, 'FAIL_QTY': 0
        }

    def get_result(self, workordno):
        params = {'WORKORDNO': workordno}
        q = self.mapper.get_query('selectProductionResult', params)
        values = tuple(params.get(name) for name in q['params'])
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(q['query'], values)
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return rows

    def get_history(self, workordno):
        params = {'WORKORDNO': workordno}
        q = self.mapper.get_query('selectProductionHistory', params)
        values = tuple(params.get(name) for name in q['params'])
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(q['query'], values)
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return rows

    def get_defect(self, workordno):
        params = {'WORKORDNO': workordno}
        q = self.mapper.get_query('selectDefectHistory', params)
        values = tuple(params.get(name) for name in q['params'])
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(q['query'], values)
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return rows

    def change_status(self, workordno, status):
        params = {'WORKORDNO': workordno, 'ORDSTATE': status}
        q = self.mapper.get_query('updateWorkorderStatus', params)
        values = tuple(params.get(name) for name in q['params'])
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(q['query'], values)
        affected = cursor.rowcount
        
        conn.commit()
        conn.close()
        return affected > 0

    def save_result(self, data):
        """실적 등록 (LOT 생성, 불량 등록 및 투입 자재 내역 차감)"""
        workordno = data.get('WORKORDNO')
        prod_qty = data.get('PROD_QTY', 0)
        fail_qty = data.get('FAIL_QTY', 0)
        
        if prod_qty <= 0:
            return False

        import datetime
        now = datetime.datetime.now()
        date_prefix = now.strftime('%y%m%d') # YYMMDD (6자리)

        # 마스터 정보 조회
        conn = get_db_connection()
        cursor = conn.cursor()

        # 0. LOT 번호 채번 (L + YYMMDDHHMMSS)
        lot_no = f"L{now.strftime('%y%m%d%H%M%S')}"

        cursor.execute("SELECT PARTNO, LINECD, PROCESSCD, SHIFT FROM TBL_PROD_WORKORDER WHERE WORKORDNO = %s", (workordno,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return False
        
        part_no, line_cd, process_cd, shift = row
        
        # 품목 단위 조회
        cursor.execute("SELECT UNIT FROM TBL_COM_GOODS WHERE PARTNO = %s", (part_no,))
        unit_row = cursor.fetchone()
        unit = unit_row[0] if unit_row else 'EA'

        # 1. 실적 등록 (신규 LOT 생성)
        good_qty = prod_qty - fail_qty
        if good_qty < 0: good_qty = 0 # 안전장치
        
        res_params = {
            'LOTNO': lot_no, 'WORKORDNO': workordno, 'PARTNO': part_no,
            'LOTQTY': good_qty, 'UNIT': unit, 'LINECD': line_cd,
            'PROCESSCD': process_cd, 'SHIFT': shift,
            'LOCATIONCODE': 'LOC001', 'WAREHOUSECODE': 'WH001'
        }
        q_res = self.mapper.get_query('insertProductionResult', res_params)
        cursor.execute(q_res['query'], tuple(res_params.get(n) for n in q_res['params']))

        # 1-1. 생산 실적 재고 이력 추가 (입고 처리)
        import datetime
        now = datetime.datetime.now()
        hist_no = f"H{now.strftime('%Y%m%d%H%M%S%f')[:17]}"
        cursor.execute("""
            INSERT INTO TBL_PROD_STOCK_HISTORY (
                LOTNO, LOCATIONCODE, STOCKHISTORYNO, QTY, 
                STOCKCHANGEGUBUN, CHANGEDAY, REMARK, REF_NO, 
                REGUSERID, REGDTM
            ) VALUES (%s, %s, %s, %s, '생산', %s, '현장생산완료', %s, 1, GETDATE())
        """, (lot_no, 'LOC001', hist_no, good_qty, now.strftime('%Y-%m-%d'), workordno))

        # 1-2. 실제 재고 테이블 반영
        cursor.execute("INSERT INTO TBL_PROD_STOCK (LOTNO, LOCATIONCODE, STOCKQTY) VALUES (%s, %s, %s)", (lot_no, 'LOC001', good_qty))

        # 2. 불량 등록
        if fail_qty > 0:
            fail_params = {'LOTNO': lot_no, 'FAILQTY': fail_qty}
            q_fail = self.mapper.get_query('insertFailQty', fail_params)
            cursor.execute(q_fail['query'], tuple(fail_params.get(n) for n in q_fail['params']))

        # 3. 투입된 자재 내역 차감 (생산실적수량 만큼)
        # 투입된 고유 품번들 조회
        cursor.execute("""
            SELECT DISTINCT S.PARTNO 
            FROM TBL_PROD_STOCK_HISTORY H
            JOIN TBL_PROD_LOTSTATE S ON H.LOTNO = S.LOTNO
            WHERE H.REF_NO = %s AND H.STOCKCHANGEGUBUN = '투입'
        """, (workordno,))
        input_parts = [r[0] for r in cursor.fetchall()]

        for child_part in input_parts:
            # BOM 소요량 조회 (SUM 처리 및 USEYN 체크)
            cursor.execute("""
                SELECT SUM(REQQTY) 
                FROM TBL_COM_BOM 
                WHERE PAR_PARTNO = %s AND CHILD_PARTNO = %s AND USEYN = 1
            """, (part_no, child_part))
            bom_row = cursor.fetchone()
            req_qty = bom_row[0] if bom_row and bom_row[0] is not None else 0
            
            if req_qty <= 0:
                continue
            
            needed = prod_qty * req_qty
            
            # 해당 품번의 투입 내역 조회 (FIFO)
            cursor.execute("""
                SELECT H.STOCKHISTORYNO, H.QTY, H.LOTNO, H.LOCATIONCODE
                FROM TBL_PROD_STOCK_HISTORY H
                JOIN TBL_PROD_LOTSTATE S ON H.LOTNO = S.LOTNO
                WHERE H.REF_NO = %s AND S.PARTNO = %s AND H.STOCKCHANGEGUBUN = '투입'
                ORDER BY H.REGDTM ASC
            """, (workordno, child_part))
            inputs = cursor.fetchall()
            
            for h_no, h_qty, m_lot, m_loc in inputs:
                if needed <= 0: break
                abs_qty = abs(h_qty)
                consume_qty = 0
                
                if abs_qty <= needed:
                    cursor.execute("DELETE FROM TBL_PROD_STOCK_HISTORY WHERE STOCKHISTORYNO = %s", (h_no,))
                    consume_qty = abs_qty
                    needed -= abs_qty
                else:
                    new_qty = (abs_qty - needed) * -1
                    cursor.execute("UPDATE TBL_PROD_STOCK_HISTORY SET QTY = %s WHERE STOCKHISTORYNO = %s", (new_qty, h_no))
                    consume_qty = needed
                    needed = 0
                
                # 실제 자재 재고 차감 로직 제거 (자재투입 시 이미 차감되므로 HISTORY만 관리)

        conn.commit()
        conn.close()
        return True

    def cancel_production(self, workordno):
        """생산 취소 (상태를 NEW로 돌리고 관련 실적 삭제)"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. 해당 작지의 LOT 목록 조회
        cursor.execute("SELECT LOTNO FROM TBL_PROD_LOTSTATE WHERE WORKORDNO = %s", (workordno,))
        lots = [r[0] for r in cursor.fetchall()]
        
        if lots:
            # 2. 불량 내역 삭제
            placeholders = ','.join(['%s'] * len(lots))
            cursor.execute(f"DELETE FROM TBL_PROD_FAILQTY WHERE LOTNO IN ({placeholders})", tuple(lots))
            # 2-1. 재고 데이터 삭제
            cursor.execute(f"DELETE FROM TBL_PROD_STOCK WHERE LOTNO IN ({placeholders})", tuple(lots))
            # 3. LOT 실적 삭제
            cursor.execute(f"DELETE FROM TBL_PROD_LOTSTATE WHERE WORKORDNO = %s", (workordno,))
        
        # 4. 상태 복구
        params = {'WORKORDNO': workordno, 'ORDSTATE': 'NEW'}
        q = self.mapper.get_query('updateWorkorderStatus', params)
        cursor.execute(q['query'], tuple(params.get(n) for n in q['params']))
        
        conn.commit()
        conn.close()
        return True


field_service = FieldService()
