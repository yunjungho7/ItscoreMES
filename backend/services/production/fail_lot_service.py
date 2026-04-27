"""불량관리 서비스"""
from db.xml_mapper import XMLMapper
from db.connection import get_db_connection
import math
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class FailLotService:
    def __init__(self):
        self.mapper = XMLMapper(os.path.join(BASE_DIR, 'sql/production/fail_lot.xml'))

    def get_all(self, start_date=None, end_date=None, plant_cd=None, lot_no=None, fail_gubuns=None, page=1, size=50):
        params = {}
        if start_date: params['start_date'] = start_date
        if end_date: params['end_date'] = end_date
        if plant_cd: params['plant_cd'] = plant_cd
        if lot_no: params['lot_no'] = f'%{lot_no}%'
        
        # In절 처리를 위해 문자열 결합 (간이 처리)
        if fail_gubuns:
            gubun_list = fail_gubuns.split(',')
            quoted = [f"'{g.strip()}'" for g in gubun_list if g.strip()]
            if quoted:
                params['fail_gubun_list'] = ','.join(quoted)

        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Count
        q = self.mapper.get_query('countFailLot', params)
        # XMLMapper가 동적 쿼리 내의 ${} 변환을 지원하지 않는 경우를 대비해 쿼리 문자열 치환
        query_str = q['query']
        if 'fail_gubun_list' in params:
            query_str = query_str.replace('${fail_gubun_list}', params['fail_gubun_list'])
            
        values = tuple(params.get(name) for name in q['params'] if name != 'fail_gubun_list')
        cursor.execute(query_str, values)
        total = cursor.fetchone()[0]

        # Select
        params['offset'] = (page - 1) * size
        params['limit'] = size
        q = self.mapper.get_query('selectFailLot', params)
        query_str = q['query']
        if 'fail_gubun_list' in params:
            query_str = query_str.replace('${fail_gubun_list}', params['fail_gubun_list'])
        values = tuple(params.get(name) for name in q['params'] if name != 'fail_gubun_list')
        
        cursor.execute(query_str, values)
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return {"data": rows, "total": total, "page": page, "totalPages": math.ceil(total / size) if total else 0}

    def process_fail_qty(self, items: list, action: str):
        # action: 'recover'(양품처리), 'scrap'(폐기처리)
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            for item in items:
                item['REMARK'] = f"[{action}] " + str(item.get('REMARK', ''))
                
                # 1. History 저장
                q1 = self.mapper.get_query('insertFailQtyHistory', item)
                v1 = tuple(item.get(name) for name in q1['params'])
                cursor.execute(q1['query'], v1)
                
                # 2. 기존 불량 삭제
                q2 = self.mapper.get_query('deleteFailQty', item)
                v2 = tuple(item.get(name) for name in q2['params'])
                cursor.execute(q2['query'], v2)
                
                # 양품처리(recover)의 경우 TBL_PROD_PRODINFO 등에 수량 복구하는 로직이 추가될 수 있음.
                # 현재는 이력 이동 및 삭제까지만 수행.
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

fail_lot_service = FailLotService()
