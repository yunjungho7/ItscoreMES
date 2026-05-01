"""생산현황 서비스"""
from db.xml_mapper import XMLMapper
from db.connection import get_db_connection
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class StatusService:
    def __init__(self):
        self.mapper = XMLMapper(os.path.join(BASE_DIR, 'sql/production/status.xml'))

    def get_results(self, workordno):
        params = {'WORKORDNO': workordno}
        q = self.mapper.get_query('selectResults', params)
        values = tuple(params.get(name) for name in q['params'])
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(q['query'], values)
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        
        return rows

    def cancel_result(self, lotno):
        params = {'LOTNO': lotno}
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # 0. 실적 정보(WORKORDNO, PARTNO, LOTQTY) 조회 (자재 복원을 위해)
            cursor.execute("""
                SELECT WORKORDNO, PARTNO, LOTQTY 
                FROM TBL_PROD_LOTSTATE 
                WHERE LOTNO = %s
            """, (lotno,))
            res_row = cursor.fetchone()
            
            if res_row:
                workordno, part_no, prod_qty = res_row
                
                # 0-1. 해당 실적에 의해 차감되었던 자재 복원 시도
                # (현 시스템 구조상 '투입' 이력의 QTY를 다시 늘려줌)
                # 투입된 품번들 조회
                cursor.execute("""
                    SELECT CHILD_PARTNO, SUM(REQQTY) 
                    FROM TBL_COM_BOM 
                    WHERE PAR_PARTNO = %s AND USEYN = 1
                    GROUP BY CHILD_PARTNO
                """, (part_no,))
                bom_items = cursor.fetchall()
                
                for child_part, req_qty in bom_items:
                    restore_qty = prod_qty * req_qty
                    if restore_qty <= 0: continue
                    
                    # 해당 작지의 '투입' 이력 중 가장 최근 것 하나에 수량 복원
                    # (FIFO의 역순으로 복원하는 것이 정확하지만, 일단 하나에 합산)
                    cursor.execute("""
                        SELECT TOP 1 STOCKHISTORYNO, QTY 
                        FROM TBL_PROD_STOCK_HISTORY 
                        WHERE REF_NO = %s AND LOTNO IN (
                            SELECT LOTNO FROM TBL_PROD_LOTSTATE WHERE PARTNO = %s
                        ) AND STOCKCHANGEGUBUN = '투입'
                        ORDER BY REGDTM DESC
                    """, (workordno, child_part))
                    hist_row = cursor.fetchone()
                    if hist_row:
                        h_no, h_qty = hist_row
                        new_h_qty = h_qty - restore_qty # QTY가 음수이므로 빼면 절대값이 커짐? 아니, 복원이므로 0에 가깝게 (더함)
                        # 아, QTY는 -100 형태. 복원하면 -80이 되어야 함. 그래서 +20 해야 함.
                        new_h_qty = h_qty + restore_qty
                        cursor.execute("UPDATE TBL_PROD_STOCK_HISTORY SET QTY = %s WHERE STOCKHISTORYNO = %s", (new_h_qty, h_no))

            # 1. 불량 데이터 삭제
            cursor.execute("DELETE FROM TBL_PROD_FAILQTY WHERE LOTNO = %s", (lotno,))
            
            # 2. 재고 데이터 삭제
            cursor.execute("DELETE FROM TBL_PROD_STOCK WHERE LOTNO = %s", (lotno,))

            # 3. 실적 데이터 삭제 (상태 변경 대신 삭제 처리)
            cursor.execute("DELETE FROM TBL_PROD_LOTSTATE WHERE LOTNO = %s", (lotno,))
            affected = cursor.rowcount
            
            conn.commit()
            return affected > 0
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

status_service = StatusService()
