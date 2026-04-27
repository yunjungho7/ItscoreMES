"""작업일보 서비스"""
from db.xml_mapper import XMLMapper
from db.connection import get_db_connection
import math
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class DailyReportService:
    def __init__(self):
        self.mapper = XMLMapper(os.path.join(BASE_DIR, 'sql/production/daily_report.xml'))

    def get_all(self, start_date=None, end_date=None, plant_cd=None, process_cd=None, shift=None, page=1, size=50):
        params = {}
        if start_date: params['start_date'] = start_date
        if end_date: params['end_date'] = end_date
        if plant_cd: params['plant_cd'] = plant_cd
        if process_cd: params['process_cd'] = process_cd
        if shift: params['shift'] = shift

        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Count
        q = self.mapper.get_query('countDailyReport', params)
        values = tuple(params.get(name) for name in q['params'])
        cursor.execute(q['query'], values)
        total = cursor.fetchone()[0]

        # Select
        params['offset'] = (page - 1) * size
        params['limit'] = size
        q = self.mapper.get_query('selectDailyReport', params)
        values = tuple(params.get(name) for name in q['params'])
        cursor.execute(q['query'], values)
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return {"data": rows, "total": total, "page": page, "totalPages": math.ceil(total / size) if total else 0}

daily_report_service = DailyReportService()
