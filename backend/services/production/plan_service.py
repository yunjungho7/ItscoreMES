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
        """기준월의 생산계획을 일자별로 피벗하여 반환"""
        if not base_date:
            base_date = date.today().strftime('%Y-%m-%d')

        year, month = int(base_date[:4]), int(base_date[5:7])
        days_in_month = monthrange(year, month)[1]
        start = f'{year}-{month:02d}-01'
        end = f'{year}-{month:02d}-{days_in_month:02d}'

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

        # 품번별 피벗
        pivot = {}
        for r in rows:
            key = r['PARTNO']
            if key not in pivot:
                pivot[key] = {
                    'PARTNO': r['PARTNO'], 'PARTNM': r.get('PARTNM',''),
                    'STANDARD': r.get('STANDARD',''), 'UNIT': r.get('UNIT',''),
                    'TOTAL': 0
                }
                for d in range(1, days_in_month + 1):
                    pivot[key][str(d)] = 0
            day_num = str(r['PRODUCEDT'].day) if hasattr(r['PRODUCEDT'], 'day') else str(int(str(r['PRODUCEDT'])[8:10]))
            qty = r.get('PRODUCEQTY', 0) or 0
            pivot[key][day_num] = pivot[key].get(day_num, 0) + qty
            pivot[key]['TOTAL'] = pivot[key].get('TOTAL', 0) + qty

        return {
            'data': list(pivot.VALUES ()),
            'year': year, 'month': month, 'days': days_in_month
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
