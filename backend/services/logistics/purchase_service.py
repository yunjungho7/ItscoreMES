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
        
        columns = [col[0].upper() for col in cursor.description]
        results = []
        for row in cursor.fetchall():
            row_dict = {}
            for i, value in enumerate(row):
                if isinstance(value, str):
                    try: value = value.encode('latin-1').decode('cp949')
                    except: pass
                row_dict[columns[i]] = value
            results.append(row_dict)
        conn.close()
        return results

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
        
        columns = [col[0].upper() for col in cursor.description]
        results = []
        for row in cursor.fetchall():
            row_dict = {}
            for i, value in enumerate(row):
                if isinstance(value, str):
                    try: value = value.encode('latin-1').decode('cp949')
                    except: pass
                row_dict[columns[i]] = value
            results.append(row_dict)
        conn.close()
        return results

    def create_purchase_order(self, data: dict):
        import datetime
        details = data.pop('details', [])
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 발주번호 생성
        q_num = self.mapper.get_query('selectNextOrderNum', {})
        cursor.execute(q_num['query'])
        order_num = cursor.fetchone()[0]
        if not order_num:
            order_num = f"PO{datetime.datetime.now().strftime('%Y%m%d')}-001"
            
        data['ORDERNUM'] = order_num
        data['ORDERDT'] = data.get('ORDERDT') or datetime.datetime.now().strftime('%Y-%m-%d')
        data['ADOFREQDT'] = data.get('ADOFREQDT') or data['ORDERDT']
        data['ORDERSTATE'] = 'NEW'
        data['REGUSERID'] = data.get('REGUSERID', '1')
        
        # Master 저장
        q_ins = self.mapper.get_query('insertPurchaseOrder', data)
        v_ins = tuple(data.get(name) for name in q_ins['params'])
        cursor.execute(q_ins['query'], v_ins)
        
        # Detail 저장 (동일 자재가 있을 경우 수량 합산 처리)
        aggregated_details = {}
        for d in details:
            part_no = d.get('PARTNO')
            qty = d.get('ORDERQTY')
            if qty is None:
                qty = 0
            
            if not part_no:
                continue
            
            if part_no in aggregated_details:
                aggregated_details[part_no]['ORDERQTY'] += float(qty)
            else:
                aggregated_details[part_no] = {
                    'ORDERNUM': order_num,
                    'PARTNO': part_no,
                    'ORDERQTY': float(qty),
                    'UNIT_PRICE': d.get('UNIT_PRICE', 0),
                    'ADOFREQDT': d.get('ADOFREQDT') or data['ADOFREQDT'],
                    'REMARK': d.get('REMARK', '')
                }
        
        for d in aggregated_details.values():
            dq = self.mapper.get_query('insertPurchaseOrderDetail', d)
            dv = tuple(d.get(name) for name in dq['params'])
            cursor.execute(dq['query'], dv)
            
        conn.commit()
        conn.close()
        return {"ORDERNUM": order_num}


    def get_purchase_orders(self, start_date=None, end_date=None, plant_cd=None, company_cd=None, search=None, include_completed=False):
        params = {}
        if start_date: params['start_date'] = start_date
        if end_date: params['end_date'] = end_date
        if plant_cd: params['plant_cd'] = plant_cd
        if company_cd: params['company_cd'] = company_cd
        if search: params['search'] = f'%{search}%'
        q = self.mapper.get_query('selectPurchaseOrderList', params)
        values = tuple(params.get(name) for name in q['params'])
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(q['query'], values)
        
        columns = [col[0].upper() for col in cursor.description]
        results = []
        for row in cursor.fetchall():
            row_dict = {}
            for i, value in enumerate(row):
                if isinstance(value, str):
                    try: value = value.encode('latin-1').decode('cp949')
                    except: pass
                row_dict[columns[i]] = value
            results.append(row_dict)
        conn.close()

        # Python 단에서 직접 COMPLETED 필터링 (XML 매퍼 조건 불안정 대비)
        if not include_completed:
            results = [r for r in results if r.get('ORDERSTATE') != 'COMPLETED']

        return results

    def get_purchase_order_details(self, order_num):
        params = {'ORDERNUM': order_num}
        q = self.mapper.get_query('selectPurchaseOrderDetailList', params)
        values = tuple(params.get(name) for name in q['params'])
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(q['query'], values)
        
        columns = [col[0].upper() for col in cursor.description]
        results = []
        for row in cursor.fetchall():
            row_dict = {}
            for i, value in enumerate(row):
                if isinstance(value, str):
                    try: value = value.encode('latin-1').decode('cp949')
                    except: pass
                row_dict[columns[i]] = value
            results.append(row_dict)
        conn.close()
        return results

purchase_service = PurchaseService()
