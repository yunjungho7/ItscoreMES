"""검사항목 서비스"""
from db.xml_mapper import XMLMapper
from db.connection import get_db_connection
import math
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class InspItemService:
    def __init__(self):
        self.mapper = XMLMapper(os.path.join(BASE_DIR, 'sql/inspection/insp_item.xml'))

    def get_all(self, plant_cd=None, insp_tp=None, item_gubun=None, test_item_gp=None, test_item=None, gauge=None, use_yn=None, page=1, size=50):
        params = {}
        if plant_cd: params['plant_cd'] = plant_cd
        if insp_tp: params['insp_tp'] = insp_tp
        if item_gubun: params['item_gubun'] = item_gubun
        if test_item_gp: params['test_item_gp'] = test_item_gp
        if test_item: params['test_item'] = f'%{test_item}%'
        if gauge: params['gauge'] = f'%{gauge}%'
        if use_yn is not None: params['use_yn'] = use_yn

        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Count
        q = self.mapper.get_query('countInspItem', params)
        values = tuple(params.get(name) for name in q['params'])
        cursor.execute(q['query'], values)
        total = cursor.fetchone()[0]

        # Select
        params['offset'] = (page - 1) * size
        params['limit'] = size
        q = self.mapper.get_query('selectInspItem', params)
        values = tuple(params.get(name) for name in q['params'])
        
        cursor.execute(q['query'], values)
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # boolean conversion for Vue
        for r in rows:
            r['USEYN'] = bool(r['USEYN'])
        
        conn.close()
        return {"data": rows, "total": total, "page": page, "totalPages": math.ceil(total / size) if total else 0}

    def save(self, data: dict):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            code = data.get('CODE')
            is_new = not bool(code)

            # USEYN 변환 (boolean -> 1/0)
            use_yn_val = 1 if data.get('USEYN', True) else 0

            # 파라미터 매핑
            params = {
                'PLANTCD': data.get('PLANTCD', 'P001'), # Default plant
                'INSP_TP': data.get('INSP_TP', ''),
                'ITEMGUBUN': data.get('ITEMGUBUN', ''),
                'TESTITEMGP': data.get('TESTITEMGP', ''),
                'TESTITEM': data.get('TESTITEM', ''),
                'GAUGE': data.get('GAUGE', ''),
                'STANDARD': data.get('STANDARD', ''),
                'USEYN': use_yn_val,
                'FAILTYPE': data.get('FAILTYPE', ''),
                'FAILBREAKDOWN': data.get('FAILBREAKDOWN', '')
            }

            if is_new:
                # 채번 로직
                date_str = datetime.now().strftime("%Y%m%d")
                q_code = self.mapper.get_query('getNewCode', {'date_str': date_str})
                cursor.execute(q_code['query'], (date_str, date_str))
                new_code = cursor.fetchone()[0]
                
                params['CODE'] = new_code
                
                q = self.mapper.get_query('insertInspItem', params)
                values = tuple(params.get(name) for name in q['params'])
                cursor.execute(q['query'], values)
                code = new_code
            else:
                params['CODE'] = code
                # 단건 존재 여부 확인 (옵션)
                q = self.mapper.get_query('updateInspItem', params)
                values = tuple(params.get(name) for name in q['params'])
                cursor.execute(q['query'], values)
                
            conn.commit()
            return {"status": "success", "code": code}
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

insp_item_service = InspItemService()
