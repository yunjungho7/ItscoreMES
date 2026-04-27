"""작업지시 서비스"""
from db.xml_mapper import XMLMapper
from db.connection import get_db_connection
import math
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class WorkOrderService:
    def __init__(self):
        self.mapper = XMLMapper(os.path.join(BASE_DIR, 'sql/production/workorder.xml'))

    def get_all(self, start_date=None, end_date=None, plant_cd=None, shift=None,
                ord_state=None, search=None, page=1, size=50):
        params = {}
        if start_date: params['start_date'] = start_date
        if end_date: params['end_date'] = end_date
        if plant_cd: params['plant_cd'] = plant_cd
        if shift: params['shift'] = shift
        if ord_state: params['ord_state'] = ord_state
        if search: params['search'] = f'%{search}%'

        conn = get_db_connection()
        cursor = conn.cursor()
        q = self.mapper.get_query('countAll', params)
        values = tuple(params.get(name) for name in q['params'])
        cursor.execute(q['query'], values)
        total = cursor.fetchone()[0]

        params['offset'] = (page - 1) * size
        params['limit'] = size
        q = self.mapper.get_query('selectAll', params)
        values = tuple(params.get(name) for name in q['params'])
        cursor.execute(q['query'], values)
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return {"data": rows, "total": total, "page": page, "totalPages": math.ceil(total / size) if total else 0}

    def get_children(self, par_workordno):
        params = {'PAR_WORKORDNO': par_workordno}
        q = self.mapper.get_query('selectChildren', params)
        values = tuple(params.get(name) for name in q['params'])
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(q['query'], values)
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return rows

    def get_next_num(self):
        q = self.mapper.get_query('selectNextNum', {})
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(q['query'])
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else 'WO00000000-001'

    def create(self, data: dict):
        wo_no = self.get_next_num()
        data['WORKORDNO'] = wo_no
        data.setdefault('ORDSTATE', 'NEW')
        data.setdefault('REGUSERID', 1)
        data.setdefault('EDITUSERID', 1)
        data.setdefault('PAR_WORKORDNO', None)
        data.setdefault('REMARK', '')

        q = self.mapper.get_query('insert', data)
        values = tuple(data.get(name) for name in q['params'])
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(q['query'], values)
        conn.commit()
        conn.close()
        return {"WORKORDNO": wo_no}

    def update(self, workordno, data: dict):
        data['WORKORDNO'] = workordno
        data.setdefault('EDITUSERID', 1)
        q = self.mapper.get_query('update', data)
        values = tuple(data.get(name) for name in q['params'])
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(q['query'], values)
        conn.commit()
        conn.close()
        return {"WORKORDNO": workordno}

    def delete(self, workordno):
        params = {'WORKORDNO': workordno, 'EDITUSERID': 1}
        q = self.mapper.get_query('softDelete', params)
        values = tuple(params.get(name) for name in q['params'])
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(q['query'], values)
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0


workorder_service = WorkOrderService()
