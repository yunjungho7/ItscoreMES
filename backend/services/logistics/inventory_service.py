"""재고관리 서비스"""
from db.xml_mapper import XMLMapper
from db.connection import get_db_connection
import math
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class InventoryService:
    def __init__(self):
        self.mapper = XMLMapper(os.path.join(BASE_DIR, 'sql/logistics/inventory.xml'))

    def get_all(self, plant_cd=None, warehouse_cd=None, line_cd=None, process_cd=None,
                part_type=None, lot_no=None, location_cd=None, search=None, page=1, size=50):
        params = {}
        if plant_cd: params['plant_cd'] = plant_cd
        if warehouse_cd: params['warehouse_cd'] = warehouse_cd
        if line_cd: params['line_cd'] = line_cd
        if process_cd: params['process_cd'] = process_cd
        if part_type: params['part_type'] = part_type
        if lot_no: params['lot_no'] = lot_no
        if location_cd: params['location_cd'] = location_cd
        if search: params['search'] = f'%{search}%'
        conn = get_db_connection()
        cursor = conn.cursor()
        q = self.mapper.get_query('countAll', params)
        values = tuple(params.get(name) for name in q['params'])
        cursor.execute(q['query'], values)
        total = cursor.fetchone()[0]
        params['offset'] = (page - 1) * size
        params['limit'] = size
        q = self.mapper.get_query('selectAll', params)
        values = tuple(params.get(name) for name in q['params'])
        cursor.execute(q['query'], values)
        columns = [col[0].upper() for col in cursor.description]
        rows = []
        for row in cursor.fetchall():
            row_dict = {}
            for i, value in enumerate(row):
                if isinstance(value, str):
                    try: value = value.encode('latin-1').decode('cp949')
                    except: pass
                row_dict[columns[i]] = value
            rows.append(row_dict)
        conn.close()
        return {"data": rows, "total": total, "page": page, "totalPages": math.ceil(total / size) if total else 0}

    def get_detail(self, partno):
        params = {'PARTNO': partno}
        q = self.mapper.get_query('selectDetail', params)
        values = tuple(params.get(name) for name in q['params'])
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(q['query'], values)
        columns = [col[0].upper() for col in cursor.description]
        rows = []
        for row in cursor.fetchall():
            row_dict = {}
            for i, value in enumerate(row):
                if isinstance(value, str):
                    try: value = value.encode('latin-1').decode('cp949')
                    except: pass
                row_dict[columns[i]] = value
            rows.append(row_dict)
        conn.close()
        return rows

    def update_stock_qty(self, data: dict):
        q = self.mapper.get_query('updateStockQty', data)
        values = tuple(data.get(name) for name in q['params'])
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(q['query'], values)
        conn.commit()
        conn.close()
        return True

    def get_summary(self):
        q = self.mapper.get_query('selectSummary', {})
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(q['query'])
        columns = [col[0] for col in cursor.description]
        row = cursor.fetchone()
        res = dict(zip(columns, row)) if row else {"total_items": 0, "low_stock_items": 0, "critical_items": 0}
        conn.close()
        return res


inventory_service = InventoryService()
