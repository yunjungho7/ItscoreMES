"""작업지시 서비스"""
from db.xml_mapper import XMLMapper
from db.connection import get_db_connection, execute_query
import math
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class WorkOrderService:
    def __init__(self):
        self.mapper = XMLMapper(os.path.join(BASE_DIR, 'sql/production/workorder.xml'))

    def get_all(self, start_date=None, end_date=None, plant_cd=None, shift=None,
                ord_state=None, search=None, parent_only=None, page=1, size=50):
        params = {}
        if start_date: params['start_date'] = start_date
        if end_date: params['end_date'] = end_date
        if plant_cd: params['plant_cd'] = plant_cd
        if shift: params['shift'] = shift
        if ord_state: params['ord_state'] = ord_state
        if parent_only is not None: params['parent_only'] = parent_only
        if search: params['search'] = f'%{search}%'

        conn = get_db_connection()
        try:
            q_count = self.mapper.get_query('countAll', params)
            count_res = execute_query(conn, q_count, params)
            total = count_res[0].get('TOTAL', 0) if isinstance(count_res, list) and count_res else 0
            if not total and isinstance(count_res, int): total = count_res # in case execute_query returns scalar

            params['offset'] = (page - 1) * size
            params['limit'] = size
            q_select = self.mapper.get_query('selectAll', params)
            rows = execute_query(conn, q_select, params)
            
            return {
                "data": rows, 
                "total": total, 
                "page": page, 
                "totalPages": math.ceil(total / size) if total else 0
            }
        finally:
            conn.close()

    def get_children(self, par_workordno):
        params = {'PAR_WORKORDNO': par_workordno}
        q = self.mapper.get_query('selectChildren', params)
        conn = get_db_connection()
        try:
            return execute_query(conn, q, params)
        finally:
            conn.close()

    def get_next_num(self):
        q = self.mapper.get_query('selectNextNum', {})
        conn = get_db_connection()
        try:
            rows = execute_query(conn, q, {})
            if rows and isinstance(rows, list):
                # execute_query returns list of dicts for SELECT
                return rows[0].get('NEXTNUM', 'WO00000000-001')
            return 'WO00000000-001'
        finally:
            conn.close()

    def create(self, data: dict):
        wo_no = self.get_next_num()
        data['WORKORDNO'] = wo_no
        data.setdefault('ORDSTATE', 'NEW')
        data.setdefault('REGUSERID', 1)
        data.setdefault('EDITUSERID', 1)
        data.setdefault('PAR_WORKORDNO', None)
        data.setdefault('REMARK', '')

        q = self.mapper.get_query('insert', data)
        conn = get_db_connection()
        try:
            execute_query(conn, q, data)
        finally:
            conn.close()
        return {"WORKORDNO": wo_no}

    def update(self, workordno, data: dict):
        data['WORKORDNO'] = workordno
        data.setdefault('EDITUSERID', 1)
        q = self.mapper.get_query('update', data)
        conn = get_db_connection()
        try:
            execute_query(conn, q, data)
        finally:
            conn.close()
        return {"WORKORDNO": workordno}

    def delete(self, workordno):
        params = {'WORKORDNO': workordno, 'EDITUSERID': 1}
        q = self.mapper.get_query('softDelete', params)
        conn = get_db_connection()
        try:
            affected = execute_query(conn, q, params)
            return affected > 0
        finally:
            conn.close()


workorder_service = WorkOrderService()
