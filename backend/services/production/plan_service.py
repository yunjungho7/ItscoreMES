"""생산계획 서비스"""
from db.xml_mapper import XMLMapper
from db.connection import get_db_connection
import os
from datetime import date, timedelta
from calendar import monthrange

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ProducePlanService:
    def __init__(self):
        self.mapper = XMLMapper(os.path.join(BASE_DIR, 'sql/production/produceplan.xml'))

    def get_plan_list(self, plant_cd=None, base_date=None, search=None):
        """기준일의 생산계획을 14일치 피벗하여 반환"""
        if not base_date:
            base_date = date.today().strftime('%Y-%m-%d')

        base_dt = date.fromisoformat(base_date)
        days_to_show = 31
        end_dt = base_dt + timedelta(days=days_to_show - 1)
        
        start = base_date
        end = end_dt.strftime('%Y-%m-%d')

        params = {'start_date': start, 'end_date': end}
        if plant_cd: params['plant_cd'] = plant_cd
        if search: params['search'] = f'%{search}%'

        q = self.mapper.get_query('selectPlanList', params)
        values = tuple(params.get(name) for name in q['params'])
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(q['query'], values)
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()

        # dates array
        dates = [(base_dt + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days_to_show)]

        # 품번별 피벗
        pivot = {}
        for r in rows:
            key = f"{r['PARTNO']}_{r.get('ORDERNUM', '')}_{r.get('ORDERSEQ', 1)}"
            if key not in pivot:
                pivot[key] = {
                    'PARTNO': r['PARTNO'], 'PARTNM': r.get('PARTNM',''),
                    'STANDARD': r.get('STANDARD',''), 'UNIT': r.get('UNIT',''),
                    'ORDERNUM': r.get('ORDERNUM', ''), 'ORDERSEQ': r.get('ORDERSEQ', 1),
                    'STOCKQTY': r.get('STOCKQTY', 0),
                    'COMPANYNM': r.get('COMPANYNM', ''),
                    'REQQTY': r.get('REQQTY', 0),
                    'TOTAL': 0
                }
                for d in dates:
                    pivot[key][d] = 0
            
            dt_str = str(r['PRODUCEDT'])[:10]
            if dt_str in pivot[key]:
                qty = r.get('PRODUCEQTY', 0) or 0
                pivot[key][dt_str] += qty
                pivot[key]['TOTAL'] += qty

        return {
            'data': list(pivot.values()),
            'dates': dates
        }

    def upsert(self, data: dict):
        q = self.mapper.get_query('upsert', data)
        values = tuple(data.get(name) for name in q['params'])
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(q['query'], values)
        conn.commit()
        conn.close()
        return True


plan_service = ProducePlanService()
