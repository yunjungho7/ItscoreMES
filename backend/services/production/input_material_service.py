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
        
        # 실제 재고 수량 차감 (TBL_PROD_STOCK 등 반영 로직이 있다면 추가)
        # 여기서는 히스토리 기반이므로 히스토리만 쌓음
        
        conn.commit()
        conn.close()
        return True

input_material_service = InputMaterialService()
