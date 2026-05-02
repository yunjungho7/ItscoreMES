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
                    
                    # 해당 작지의 '투입/소모' 이력이 있는 LOT들 중 잔량이 가장 적은(즉, 소모된) 것부터 복원 시도
                    # 누적 저장을 위해 '생산취소_복원' 내역 추가 (음수 QTY)
                    # (간소화를 위해 해당 품번의 첫 번째 투입 LOT을 찾아 복원 레코드 추가)
                    cursor.execute("""
                        SELECT TOP 1 LOTNO, LOCATIONCODE
                        FROM TBL_PROD_STOCK_HISTORY 
                        WHERE REF_NO = %s AND LOTNO IN (
                            SELECT LOTNO FROM TBL_PROD_LOTSTATE WHERE PARTNO = %s
                        ) AND STOCKCHANGEGUBUN IN ('투입', '소모')
                        ORDER BY REGDTM DESC
                    """, (workordno, child_part))
                    hist_row = cursor.fetchone()
                    if hist_row:
                        h_lot, h_loc = hist_row
                        import datetime
                        now_restore = datetime.datetime.now()
                        r_hist_no = f"H{now_restore.strftime('%Y%m%d%H%M%S%f')[:19]}"
                        
                        # 복원이므로 음수 QTY (잔량을 다시 늘림)
                        cursor.execute("""
                            INSERT INTO TBL_PROD_STOCK_HISTORY (
                                LOTNO, LOCATIONCODE, STOCKHISTORYNO, QTY, 
                                STOCKCHANGEGUBUN, CHANGEDAY, REMARK, REF_NO, 
                                REGUSERID, REGDTM
                            ) VALUES (%s, %s, %s, %s, '생산취소_복원', %s, '실적취소복원', %s, 1, GETDATE())
                        """, (h_lot, h_loc, r_hist_no, restore_qty * -1, now_restore.strftime('%Y-%m-%d'), workordno))

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
