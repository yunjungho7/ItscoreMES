"""발주관리/생산계획 서비스"""
from db.xml_mapper import XMLMapper
from db.connection import get_db_connection
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class PurchaseService:
    def __init__(self):
        self.mapper = XMLMapper(os.path.join(BASE_DIR, 'sql/logistics/purchase.xml'))

    def get_plan_list(self, plant_cd=None, start_date=None, end_date=None, search=None):
        params = {}
        if plant_cd: params['plant_cd'] = plant_cd
        if start_date: params['start_date'] = start_date
        if end_date: params['end_date'] = end_date
        if search: params['search'] = f'%{search}%'
        q = self.mapper.get_query('selectPlanList', params)
        values = tuple(params.get(name) for name in q['params'])
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(q['query'], values)
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return rows

    def create_plan(self, data: dict):
        q = self.mapper.get_query('insertPlan', data)
        values = tuple(data.get(name) for name in q['params'])
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(q['query'], values)
        conn.commit()
        conn.close()
        return True

    def get_bom_children(self, par_partno: str):
        params = {'par_partno': par_partno}
        q = self.mapper.get_query('selectBomChildren', params)
        values = tuple(params.get(name) for name in q['params'])
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(q['query'], values)
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return rows


purchase_service = PurchaseService()
