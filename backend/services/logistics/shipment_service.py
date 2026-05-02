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
        columns = [col[0].upper() for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return rows

    def get_all(self, start_date=None, end_date=None, plant_cd=None, company_cd=None,
                order_no=None, search=None, is_performance=False, page=1, size=50):
        params = {}
        if start_date: params['start_date'] = start_date
        if end_date: params['end_date'] = end_date
        if plant_cd: params['plant_cd'] = plant_cd
        if company_cd: params['company_cd'] = company_cd
        if order_no: params['order_no'] = order_no
        if search: params['search'] = f'%{search}%'

        query_prefix = 'Performance' if is_performance else ''
        count_id = f'count{query_prefix}' if query_prefix else 'countAll'
        select_id = f'select{query_prefix}' if query_prefix else 'selectAll'

        conn = get_db_connection()
        cursor = conn.cursor()
        q_count = self.mapper.get_query(count_id, params)
        c_vals = tuple(params.get(name) for name in q_count['params'])
        cursor.execute(q_count['query'], c_vals)
        total = cursor.fetchone()[0]

        params['offset'] = (page - 1) * size
        params['limit'] = size
        q_sel = self.mapper.get_query(select_id, params)
        s_vals = tuple(params.get(name) for name in q_sel['params'])
        cursor.execute(q_sel['query'], s_vals)
        columns = [col[0].upper() for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return {"data": rows, "total": total, "page": page, "totalPages": math.ceil(total / size) if total else 0}

    def get_details(self, shipment_no, is_performance=False):
        query_id = 'selectPerformanceDetails' if is_performance else 'selectDetails'
        param_key = 'SHIPMENTNO' if is_performance else 'SHIPMENTINDICATIONNO'
        return self._exec_select(query_id, {param_key: shipment_no})

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
        columns = [col[0].lower() for col in cursor.description]
        row = cursor.fetchone()
        res = dict(zip(columns, row)) if row else {"expected_today": 0, "completed_today": 0, "pending_all": 0}
        conn.close()
        return res

    def create_shipment(self, data: dict):
        """
        출하실적 등록
        """
        import datetime
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # 1. SHIPMENTNO 생성
            today = datetime.datetime.now().strftime('%Y%m%d')
            prefix = today
            no_params = {"prefix": prefix}
            q_no = self.mapper.get_query('getNextShipmentNo', no_params)
            no_vals = tuple(no_params.get(name) for name in q_no['params'])
            cursor.execute(q_no['query'], no_vals)
            row = cursor.fetchone()
            max_no = row[0] if row and row[0] else f"{prefix}0000"
            next_seq = int(max_no[-4:]) + 1
            shipment_no = f"{prefix}{next_seq:04d}"

            # 2. 헤더 등록
            header_params = {
                "shipment_no": shipment_no,
                "shipment_indication_no": data.get('shipment_indication_no'),
                "company_cd": data.get('company_cd'),
                "unit": data.get('unit'),
                "raise_car_day": datetime.datetime.now().strftime('%Y-%m-%d'),
                "raise_car_time": datetime.datetime.now().strftime('%H:%M'),
                "plant_cd": data.get('plant_cd'),
                "shipment_gubun": "NORMAL",
                "user_id": data.get('user_id') or 1
            }
            q_ins = self.mapper.get_query('insertShipment', header_params)
            ins_vals = tuple(header_params.get(name) for name in q_ins['params'])
            cursor.execute(q_ins['query'], ins_vals)

            # 3. 상세 등록
            for lot in data.get('lots', []):
                dtl_params = {
                    "shipment_no": shipment_no,
                    "lot_no": lot.get('lot_no'),
                    "part_no": lot.get('part_no'),
                    "shipment_lot_qty": lot.get('qty')
                }
                q_dtl = self.mapper.get_query('insertShipmentDetail', dtl_params)
                dtl_vals = tuple(dtl_params.get(name) for name in q_dtl['params'])
                cursor.execute(q_dtl['query'], dtl_vals)

            conn.commit()
            return shipment_no
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()


shipment_service = ShipmentService()
