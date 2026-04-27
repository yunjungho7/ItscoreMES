"""검사성적서 서비스"""
from db.xml_mapper import XMLMapper
from db.connection import get_db_connection
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestScoreService:
    def __init__(self):
        self.mapper = XMLMapper(os.path.join(BASE_DIR, 'sql/inspection/testscore.xml'))

    def get_list(self, plant=None, test_gubun=None, prod_cd=None, part_no_nm=None, lot_no=None, start_date=None, end_date=None):
        params = {}
        if plant: params['plant'] = plant
        if test_gubun: params['test_gubun'] = test_gubun
        if prod_cd: params['prod_cd'] = prod_cd
        if part_no_nm: params['part_no_nm'] = f'%{part_no_nm}%'
        if lot_no: params['lot_no'] = f'%{lot_no}%'
        
        # Add time components for accurate date range matching
        if start_date: params['start_date'] = start_date + ' 00:00:00'
        if end_date: params['end_date'] = end_date + ' 23:59:59'

        conn = get_db_connection()
        cursor = conn.cursor()
        
        q = self.mapper.get_query('selectTestScoreList', params)
        values = tuple(params.get(name) for name in q['params'])
        cursor.execute(q['query'], values)
        
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return rows

    def get_details(self, pcode: str):
        params = {'PCODE': pcode}
        conn = get_db_connection()
        cursor = conn.cursor()
        
        q = self.mapper.get_query('selectTestScoreDetails', params)
        values = tuple(params.get(name) for name in q['params'])
        cursor.execute(q['query'], values)
        
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return rows

testscore_service = TestScoreService()
