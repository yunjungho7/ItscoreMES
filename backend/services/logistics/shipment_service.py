"""출하관리 서비스"""
from db.xml_mapper import XMLMapper
from db.connection import get_db_connection
import math
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ShipmentService:
    def __init__(self):
        self.mapper = XMLMapper(os.path.join(BASE_DIR, 'sql/logistics/shipment.xml'))

    def _exec_select(self, query_id, params):
        q = self.mapper.get_query(query_id, params)
        values = tuple(params.get(name) for name in q['params'])
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(q['query'], values)
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return rows

    def get_all(self, start_date=None, end_date=None, plant_cd=None, company_cd=None,
                order_no=None, search=None, include_done=None, page=1, size=50):
        params = {}
        if start_date: params['start_date'] = start_date
        if end_date: params['end_date'] = end_date
        if plant_cd: params['plant_cd'] = plant_cd
        if company_cd: params['company_cd'] = company_cd
        if order_no: params['order_no'] = order_no
        if search: params['search'] = f'%{search}%'
        if include_done: params['include_done'] = '1'

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

    def get_details(self, shipment_no):
        return self._exec_select('selectDetails', {'SHIPMENTINDICATIONNO': shipment_no})

    def get_order_items(self, company_cd=None, plant_cd=None, start_date=None, end_date=None):
        params = {}
        if company_cd: params['company_cd'] = company_cd
        if plant_cd: params['plant_cd'] = plant_cd
        if start_date: params['start_date'] = start_date
        if end_date: params['end_date'] = end_date
        return self._exec_select('selectOrderItems', params)

    def get_next_num(self):
        q = self.mapper.get_query('selectNextNum', {})
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(q['query'])
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else 'SH00000000-001'

    def create(self, data: dict):
        details = data.pop('details', [])
        sh_no = self.get_next_num()
        data['SHIPMENTINDICATIONNO'] = sh_no
        data.setdefault('SHIPMENTSTATUS', 'NEW')
        data.setdefault('REGUSERID', 1)
        data.setdefault('REMARK', '')

        q = self.mapper.get_query('insert', data)
        values = tuple(data.get(name) for name in q['params'])
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(q['query'], values)

        for i, d in enumerate(details):
            d['SHIPMENTINDICATIONNO'] = sh_no
            d['SEQ'] = i + 1
            d.setdefault('SHIPMENTSTATUS', 'NEW')
            d.setdefault('SHIPMENTPLANDAY', data.get('SHIPMENTPLANDAY'))
            d.setdefault('REMARK', '')
            dq = self.mapper.get_query('insertDetail', d)
            dv = tuple(d.get(name) for name in dq['params'])
            cursor.execute(dq['query'], dv)

        conn.commit()
        conn.close()
        return {"SHIPMENTINDICATIONNO": sh_no}

    def complete(self, shipment_no):
        params = {'SHIPMENTINDICATIONNO': shipment_no, 'EDITUSERID': 1}
        q = self.mapper.get_query('completeShipment', params)
        values = tuple(params.get(name) for name in q['params'])
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(q['query'], values)
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0

    def delete(self, shipment_no):
        params = {'SHIPMENTINDICATIONNO': shipment_no, 'EDITUSERID': 1}
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
        res = dict(zip(columns, row)) if row else {"expected_today": 0, "completed_today": 0, "pending_all": 0}
        conn.close()
        return res


shipment_service = ShipmentService()
