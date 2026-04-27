"""입고관리 서비스"""
from db.xml_mapper import XMLMapper
from db.connection import get_db_connection
import math
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ReceiveService:
    def __init__(self):
        self.mapper = XMLMapper(os.path.join(BASE_DIR, 'sql/logistics/receive.xml'))

    def get_all(self, start_date=None, end_date=None, plant_cd=None, company_cd=None, order_num=None, search=None, page=1, size=50):
        params = {}
        if start_date: params['start_date'] = start_date
        if end_date: params['end_date'] = end_date
        if plant_cd: params['plant_cd'] = plant_cd
        if company_cd: params['company_cd'] = company_cd
        if order_num: params['order_num'] = order_num
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

    def get_details(self, warehouse_num):
        params = {'WAREHOUSENUM': warehouse_num}
        q = self.mapper.get_query('selectDetails', params)
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
        return row[0] if row else 'WH00000000-001'

    def create(self, data: dict):
        details = data.pop('details', [])
        wh_num = self.get_next_num()
        data['WAREHOUSENUM'] = wh_num
        data['WHSTATE'] = 'RECEIVED'
        data['INTIME'] = ''
        q = self.mapper.get_query('insert', data)
        values = tuple(data.get(name) for name in q['params'])
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(q['query'], values)
        for i, d in enumerate(details):
            d['WAREHOUSENUM'] = wh_num
            d['WHDETAILNO'] = i + 1
            d['INDAY'] = data.get('INDAY')
            if not d.get('LOTNO'):
                d['LOTNO'] = f"L{wh_num[-3:]}-{i+1:03d}"
            dq = self.mapper.get_query('insertDetail', d)
            dv = tuple(d.get(name) for name in dq['params'])
            cursor.execute(dq['query'], dv)
        conn.commit()
        conn.close()
        return {"WAREHOUSENUM": wh_num}

    def delete(self, warehouse_num):
        params = {'WAREHOUSENUM': warehouse_num, 'EDITUSERID': '1'}
        q = self.mapper.get_query('softDelete', params)
        values = tuple(params.get(name) for name in q['params'])
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(q['query'], values)
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0

    def get_summary(self):
        q = self.mapper.get_query('selectSummary', {})
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(q['query'])
        columns = [col[0] for col in cursor.description]
        row = cursor.fetchone()
        res = dict(zip(columns, row)) if row else {"expected_today": 0, "in_progress": 0, "quality_pending": 0}
        conn.close()
        return res


receive_service = ReceiveService()
