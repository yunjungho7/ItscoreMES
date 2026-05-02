"""투입자재 서비스"""
from db.xml_mapper import XMLMapper
from db.connection import get_db_connection
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class InputMaterialService:
    def __init__(self):
        self.mapper = XMLMapper(os.path.join(BASE_DIR, 'sql/production/input_material.xml'))

    def get_input_materials(self, workordno):
        params = {'WORKORDNO': workordno}
        q = self.mapper.get_query('selectInputMaterials', params)
        values = tuple(params.get(name) for name in q['params'])
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(q['query'], values)
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        
        return rows

    def save_input(self, data):
        """자재 투입 실적 저장"""
        import datetime
        now = datetime.datetime.now()
        hist_no = f"H{now.strftime('%Y%m%d%H%M%S%f')[:19]}"
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # 0. 중복 투입 방지 및 재고 확인
            cursor.execute("SELECT LOTQTY, LOCATIONCODE FROM TBL_PROD_LOTSTATE WHERE LOTNO = %s", (data['MAT_LOTNO'],))
            row = cursor.fetchone()
            if not row:
                conn.close()
                return False
            
            lot_qty, loc_cd = row
            input_qty = data['INPUT_QTY']
            
            if lot_qty < input_qty:
                # 가용 재고 부족 시 실패 처리 (또는 남은 만큼만 투입하는 정책 결정 필요)
                # 여기서는 엄격하게 부족하면 실패 처리
                conn.close()
                return False

            params = {
                'WORKORDNO': data['WORKORDNO'],
                'MAT_LOTNO': data['MAT_LOTNO'],
                'INPUT_QTY': input_qty,
                'LOCATIONCODE': loc_cd,
                'STOCKHISTORYNO': hist_no,
                'REMARK': data.get('REMARK', '')
            }
            
            q = self.mapper.get_query('insertInputMaterial', params)
            cursor.execute(q['query'], tuple(params.get(n) for n in q['params']))
            
            # 실제 재고 수량 차감 (TBL_PROD_LOTSTATE 및 TBL_PROD_STOCK 반영)
            cursor.execute("UPDATE TBL_PROD_LOTSTATE SET LOTQTY = LOTQTY - %s WHERE LOTNO = %s", (input_qty, data['MAT_LOTNO']))
            cursor.execute("UPDATE TBL_PROD_STOCK SET STOCKQTY = STOCKQTY - %s WHERE LOTNO = %s AND LOCATIONCODE = %s", (input_qty, data['MAT_LOTNO'], loc_cd))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def delete_input(self, data):
        """자재 투입 실적 삭제(취소) 및 재고 복원 - 누계 관리 방식"""
        params = {
            'WORKORDNO': data['WORKORDNO'],
            'MAT_LOTNO': data['MAT_LOTNO']
        }
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 삭제 전 투입되었던 잔량 및 위치 확인 (누계 기준)
        cursor.execute("""
            SELECT SUM(QTY), MAX(LOCATIONCODE) 
            FROM TBL_PROD_STOCK_HISTORY 
            WHERE REF_NO = %s AND LOTNO = %s AND STOCKCHANGEGUBUN IN ('투입', '소모', '투입취소', '생산취소_복원')
        """, (data['WORKORDNO'], data['MAT_LOTNO']))
        row = cursor.fetchone()
        
        if row and row[0] is not None and row[0] < 0:
            remaining_qty = row[0]
            input_qty = abs(remaining_qty)
            loc_cd = row[1]
            
            # 1. 히스토리 삭제 대신 '투입취소' 추가 (누적)
            import datetime
            now = datetime.datetime.now()
            hist_no = f"H{now.strftime('%Y%m%d%H%M%S%f')[:19]}"
            
            # 히스토리 추가 (양수 QTY로 잔량 0화)
            cursor.execute("""
                INSERT INTO TBL_PROD_STOCK_HISTORY (
                    LOTNO, LOCATIONCODE, STOCKHISTORYNO, QTY, 
                    STOCKCHANGEGUBUN, CHANGEDAY, REMARK, REF_NO, 
                    REGUSERID, REGDTM
                ) VALUES (%s, %s, %s, %s, '투입취소', %s, '투입취소', %s, 1, GETDATE())
            """, (data['MAT_LOTNO'], loc_cd, hist_no, input_qty, now.strftime('%Y-%m-%d'), data['WORKORDNO']))

            # 2. 실제 재고 복원
            cursor.execute("UPDATE TBL_PROD_LOTSTATE SET LOTQTY = LOTQTY + %s WHERE LOTNO = %s", (input_qty, data['MAT_LOTNO']))
            cursor.execute("UPDATE TBL_PROD_STOCK SET STOCKQTY = STOCKQTY + %s WHERE LOTNO = %s AND LOCATIONCODE = %s", (input_qty, data['MAT_LOTNO'], loc_cd))

        conn.commit()
        conn.close()
        return True

input_material_service = InputMaterialService()
