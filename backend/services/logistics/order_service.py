"""수주관리 서비스"""
from db.xml_mapper import XMLMapper
from db.connection import get_db_connection
import math
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class OrderService:
    def __init__(self):
        self.mapper = XMLMapper(os.path.join(BASE_DIR, 'sql/logistics/order.xml'))

    def get_all(self, start_date=None, end_date=None, plant_cd=None, company_cd=None, search=None, page=1, size=50):
        params = {}
        if start_date: params['start_date'] = start_date
        if end_date: params['end_date'] = end_date
        if plant_cd: params['plant_cd'] = plant_cd
        if company_cd: params['company_cd'] = company_cd
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
        columns = [col[0].upper() for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return {"data": rows, "total": total, "page": page, "totalPages": math.ceil(total / size) if total else 0}

    def get_by_id(self, order_no):
        params = {'ORDERNO': order_no}
        q = self.mapper.get_query('selectById', params)
        values = tuple(params.get(name) for name in q['params'])
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(q['query'], values)
        columns = [col[0].upper() for col in cursor.description]
        row = cursor.fetchone()
        conn.close()
        return dict(zip(columns, row)) if row else None

    def get_details(self, order_no):
        params = {'ORDERNO': order_no}
        q = self.mapper.get_query('selectDetails', params)
        values = tuple(params.get(name) for name in q['params'])
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(q['query'], values)
        columns = [col[0].upper() for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return rows

    def create(self, data: dict):
        details = data.pop('details', [])
        data.setdefault('REGUSERID', 1)
        data.setdefault('EDITUSERID', 1)
        data.setdefault('ORDERSTATE', 'NEW')
        conn = get_db_connection()
        cursor = conn.cursor()
        q = self.mapper.get_query('insert', data)
        values = tuple(data.get(name) for name in q['params'])
        cursor.execute(q['query'], values)
        order_no = cursor.fetchone()[0]
        for i, d in enumerate(details):
            d['ORDERNO'] = order_no
            d['SEQ'] = i + 1
            dq = self.mapper.get_query('insertDetail', d)
            dv = tuple(d.get(name) for name in dq['params'])
            cursor.execute(dq['query'], dv)
        conn.commit()
        conn.close()
        return {"ORDERNO": order_no}

    def update(self, order_no, data: dict):
        details = data.pop('details', [])
        data['ORDERNO'] = order_no
        data.setdefault('EDITUSERID', 1)
        conn = get_db_connection()
        cursor = conn.cursor()
        q = self.mapper.get_query('update', data)
        values = tuple(data.get(name) for name in q['params'])
        cursor.execute(q['query'], values)
        dq = self.mapper.get_query('deleteDetails', {'ORDERNO': order_no})
        dv = tuple({'ORDERNO': order_no}.get(name) for name in dq['params'])
        cursor.execute(dq['query'], dv)
        for i, d in enumerate(details):
            d['ORDERNO'] = order_no
            d['SEQ'] = i + 1
            iq = self.mapper.get_query('insertDetail', d)
            iv = tuple(d.get(name) for name in iq['params'])
            cursor.execute(iq['query'], iv)
        conn.commit()
        conn.close()
        return {"ORDERNO": order_no}

    def delete(self, order_no):
        conn = get_db_connection()
        cursor = conn.cursor()
        params = {'ORDERNO': order_no}
        q = self.mapper.get_query('softDelete', params)
        values = tuple(params.get(name) for name in q['params'])
        cursor.execute(q['query'], values)
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0


order_service = OrderService()
