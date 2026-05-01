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

    def get_next_num(self, type=None, conn=None):
        query_id = 'selectNextNum'
        if type == 'parent': query_id = 'selectNextNumParent'
        elif type == 'child': query_id = 'selectNextNumChild'
        
        q = self.mapper.get_query(query_id, {})
        
        local_conn = False
        if conn is None:
            conn = get_db_connection()
            local_conn = True
            
        try:
            rows = execute_query(conn, q, {})
            if rows and isinstance(rows, list):
                default_prefix = 'WO'
                if type == 'parent': default_prefix = 'WP'
                elif type == 'child': default_prefix = 'WC'
                import datetime
                default_num = f"{default_prefix}{datetime.datetime.now().strftime('%Y%m%d')}-001"
                return rows[0].get('NEXTNUM', default_num)
            return 'WO00000000-001'
        finally:
            if local_conn:
                conn.close()

    def create(self, data: dict, conn=None):
        # PAR_WORKORDNO 존재 여부로 parent/child 구분
        is_child = data.get('PAR_WORKORDNO') is not None and str(data.get('PAR_WORKORDNO')).strip() != ''
        wo_type = 'child' if is_child else 'parent'
        
        local_conn = False
        if conn is None:
            conn = get_db_connection()
            local_conn = True
            
        try:
            wo_no = self.get_next_num(type=wo_type, conn=conn)
            data['WORKORDNO'] = wo_no
            data.setdefault('ORDSTATE', 'NEW')
            data.setdefault('REGUSERID', 1)
            data.setdefault('EDITUSERID', 1)
            data.setdefault('PAR_WORKORDNO', None)
            data.setdefault('REMARK', '')

            q = self.mapper.get_query('insert', data)
            execute_query(conn, q, data)
            return {"WORKORDNO": wo_no}
        finally:
            if local_conn:
                conn.close()

    def create_batch(self, header: dict, items: list):
        conn = get_db_connection()
        print(f"DEBUG: create_batch started. Header PARTNO: {header.get('PARTNO')}, Items count: {len(items)}")
        try:
            # 1. 상위 작업지시 생성
            header['ORDTYPE'] = 'WP작업'
            parent_res = self.create(header, conn=conn)
            parent_wo_no = parent_res["WORKORDNO"]
            print(f"DEBUG: Parent created: {parent_wo_no}")
            
            # 2. 하위 작업지시들 생성
            child_nos = []
            
            # 하위 작지 번호 채번 베이스 가져오기
            import datetime
            now_str = datetime.datetime.now().strftime('%Y%m%d')
            prefix = 'WC'
            
            # 현재 DB의 마지막 번호를 조회
            q_next = self.mapper.get_query('selectNextNumChild', {})
            res_next = execute_query(conn, q_next, {})
            
            next_num_str = res_next[0].get('NEXTNUM') if res_next else f"{prefix}{now_str}-001"
            # next_num_str 예: WC20260501-001
            try:
                base_num = int(next_num_str.split('-')[-1])
            except:
                base_num = 1
                
            for i, item in enumerate(items):
                item['PAR_WORKORDNO'] = parent_wo_no
                item.setdefault('PLANTCD', header.get('PLANTCD'))
                item['ORDTYPE'] = 'WC작업'
                item.setdefault('ORDpriority', header.get('ORDpriority', 1))
                item.setdefault('REMARK', header.get('REMARK', ''))
                
                # 수동 번호 생성 (루프 내 DB 조회 방지)
                wo_no = f"{prefix}{now_str}-{base_num + i:03d}"
                item['WORKORDNO'] = wo_no
                
                # create 대신 직접 insert 로직 (이미 번호를 생성했으므로)
                item.setdefault('ORDSTATE', 'NEW')
                item.setdefault('REGUSERID', 1)
                item.setdefault('EDITUSERID', 1)
                
                print(f"DEBUG: Creating child {i+1}/{len(items)}: {wo_no} for {item.get('PARTNO')}")
                q_ins = self.mapper.get_query('insert', item)
                execute_query(conn, q_ins, item)
                child_nos.append(wo_no)
                
            print(f"DEBUG: create_batch finished. Total children: {len(child_nos)}")
            return {
                "parent_workordno": parent_wo_no,
                "child_count": len(child_nos),
                "child_workordnos": child_nos
            }
        except Exception as e:
            print(f"ERROR: create_batch failed: {e}")
            if hasattr(conn, 'rollback'):
                conn.rollback()
            raise e
        finally:
            conn.close()

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
