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
        q = self.mapper.get_query('cancelResult', params)
        values = tuple(params.get(name) for name in q['params'])
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(q['query'], values)
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected > 0

status_service = StatusService()
