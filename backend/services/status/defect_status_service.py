"""불량현황 서비스"""
from db.xml_mapper import XMLMapper
from db.connection import get_db_connection
import math
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class DefectStatusService:
    def __init__(self):
        self.mapper = XMLMapper(os.path.join(BASE_DIR, 'sql/status/defect_status.xml'))

    def get_all(self, start_date=None, end_date=None, plant_cd=None, lot_no=None, part_no=None, process_status=None, page=1, size=50):
        params = {}
        if start_date: params['start_date'] = start_date
        if end_date: params['end_date'] = end_date
        if plant_cd: params['plant_cd'] = plant_cd
        if lot_no: params['lot_no'] = f'%{lot_no}%'
        if part_no: params['part_no'] = f'%{part_no}%'
        if process_status and process_status != '전체': params['process_status'] = process_status

        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Count
        q = self.mapper.get_query('countDefectStatus', params)
        values = tuple(params.get(name) for name in q['params'])
        cursor.execute(q['query'], values)
        total = cursor.fetchone()[0]

        # Select
        params['offset'] = (page - 1) * size
        params['limit'] = size
        q = self.mapper.get_query('selectDefectStatus', params)
        values = tuple(params.get(name) for name in q['params'])
        
        cursor.execute(q['query'], values)
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return {"data": rows, "total": total, "page": page, "totalPages": math.ceil(total / size) if total else 0}

defect_status_service = DefectStatusService()
