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
        
        # 1. 불량 데이터 삭제
        cursor.execute("DELETE FROM TBL_PROD_FAILQTY WHERE LOTNO = %s", (lotno,))
        
        # 2. 재고 데이터 삭제
        cursor.execute("DELETE FROM TBL_PROD_STOCK WHERE LOTNO = %s", (lotno,))

        # 3. 실적 데이터 삭제 (또는 취소 상태 변경)
        q = self.mapper.get_query('cancelResult', params)
        cursor.execute(q['query'], tuple(params.get(n) for n in q['params']))
        affected = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return affected > 0

status_service = StatusService()
