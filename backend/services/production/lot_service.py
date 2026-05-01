"""LOT 관리 서비스"""
from db.xml_mapper import XMLMapper
from db.connection import get_db_connection
import math
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class LotService:
    def __init__(self):
        self.mapper = XMLMapper(os.path.join(BASE_DIR, 'sql/production/lot.xml'))

    def get_all(self, start_date=None, end_date=None, lot_no=None, part_no=None, page=1, size=50):
        params = {}
        if start_date: params['start_date'] = start_date
        if end_date: params['end_date'] = end_date
        if lot_no: params['lot_no'] = f'%{lot_no}%'
        if part_no: params['part_no'] = f'%{part_no}%'

        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Count
        q = self.mapper.get_query('countAllLot', params)
        values = tuple(params.get(name) for name in q['params'])
        cursor.execute(q['query'], values)
        total = cursor.fetchone()[0]

        # Select
        params['offset'] = (page - 1) * size
        params['limit'] = size
        q = self.mapper.get_query('selectAllLot', params)
        values = tuple(params.get(name) for name in q['params'])
        cursor.execute(q['query'], values)
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return {"data": rows, "total": total, "page": page, "totalPages": math.ceil(total / size) if total else 0}

    def get_next_num(self):
        q = self.mapper.get_query('selectNextLotNum', {})
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(q['query'])
        row = cursor.fetchone()
        conn.close()
        import datetime
        default_lot = f"L{datetime.datetime.now().strftime('%y%m%d')}001"
        return row[0] if row and row[0] else default_lot

    def create(self, data: dict):
        lot_no = self.get_next_num()
        data['LOTNO'] = lot_no
        
        # Default handling
        data.setdefault('LOTTYPE', '일반')
        data.setdefault('REMARK', '')
        data.setdefault('WORKORDNO', None)
        data.setdefault('PROCESSCD', None)
        data.setdefault('LINECD', None)
        data.setdefault('SHIFT', None)

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # 1. LOT State Insert
            q1 = self.mapper.get_query('insertLotState', data)
            v1 = tuple(data.get(name) for name in q1['params'])
            cursor.execute(q1['query'], v1)
            
            # 2. LOT History Insert
            q2 = self.mapper.get_query('insertLotHistory', data)
            v2 = tuple(data.get(name) for name in q2['params'])
            cursor.execute(q2['query'], v2)
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
            
        return {"LOTNO": lot_no}

    def get_tracking(self, lotno):
        params = {'lotno': lotno}
        q = self.mapper.get_query('selectLotTracking', params)
        values = tuple(params.get(name) for name in q['params'])
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(q['query'], values)
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        
        return rows

    def get_available_lots(self, part_no):
        params = {'part_no': part_no}
        q = self.mapper.get_query('selectAvailableLots', params)
        values = tuple(params.get(name) for name in q['params'])
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(q['query'], values)
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        
        return rows

lot_service = LotService()
