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
        hist_no = f"H{now.strftime('%Y%m%d%H%M%S%f')[:17]}"
        
        # LOT 정보에서 현재 위치(LOCATIONCODE) 조회
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT LOCATIONCODE FROM TBL_PROD_LOTSTATE WHERE LOTNO = %s", (data['MAT_LOTNO'],))
        row = cursor.fetchone()
        loc_cd = row[0] if row else 'BASE'
        
        params = {
            'WORKORDNO': data['WORKORDNO'],
            'MAT_LOTNO': data['MAT_LOTNO'],
            'INPUT_QTY': data['INPUT_QTY'],
            'LOCATIONCODE': loc_cd,
            'STOCKHISTORYNO': hist_no,
            'REMARK': data.get('REMARK', '')
        }
        
        q = self.mapper.get_query('insertInputMaterial', params)
        cursor.execute(q['query'], tuple(params.get(n) for n in q['params']))
        
        # 실제 재고 수량 차감 (TBL_PROD_LOTSTATE 및 TBL_PROD_STOCK 반영)
        cursor.execute("UPDATE TBL_PROD_LOTSTATE SET LOTQTY = LOTQTY - %s WHERE LOTNO = %s", (data['INPUT_QTY'], data['MAT_LOTNO']))
        cursor.execute("UPDATE TBL_PROD_STOCK SET STOCKQTY = STOCKQTY - %s WHERE LOTNO = %s AND LOCATIONCODE = %s", (data['INPUT_QTY'], data['MAT_LOTNO'], loc_cd))
        
        conn.commit()
        conn.close()
        return True

    def delete_input(self, data):
        """자재 투입 실적 삭제 및 재고 복원"""
        params = {
            'WORKORDNO': data['WORKORDNO'],
            'MAT_LOTNO': data['MAT_LOTNO']
        }
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 삭제 전 투입되었던 수량 및 위치 확인 (복원을 위해)
        cursor.execute("SELECT ABS(QTY), LOCATIONCODE FROM TBL_PROD_STOCK_HISTORY WHERE REF_NO = %s AND LOTNO = %s AND STOCKCHANGEGUBUN = '투입'", (data['WORKORDNO'], data['MAT_LOTNO']))
        row = cursor.fetchone()
        if row:
            input_qty, loc_cd = row
            # 1. 히스토리 삭제
            q = self.mapper.get_query('deleteInputMaterial', params)
            cursor.execute(q['query'], tuple(params.get(n) for n in q['params']))
            # 2. 재고 복원
            cursor.execute("UPDATE TBL_PROD_LOTSTATE SET LOTQTY = LOTQTY + %s WHERE LOTNO = %s", (input_qty, data['MAT_LOTNO']))
            cursor.execute("UPDATE TBL_PROD_STOCK SET STOCKQTY = STOCKQTY + %s WHERE LOTNO = %s AND LOCATIONCODE = %s", (input_qty, data['MAT_LOTNO'], loc_cd))

        conn.commit()
        conn.close()
        return True

input_material_service = InputMaterialService()
