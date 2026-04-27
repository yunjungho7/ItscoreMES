"""기준서관리 서비스"""
from db.xml_mapper import XMLMapper
from db.connection import get_db_connection
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class InspStandardService:
    def __init__(self):
        self.mapper = XMLMapper(os.path.join(BASE_DIR, 'sql/inspection/insp_standard.xml'))

    def get_list(self, part_no_nm=None, part_gubun=None):
        params = {}
        if part_no_nm: params['part_no_nm'] = f'%{part_no_nm}%'
        if part_gubun: params['part_gubun'] = part_gubun

        conn = get_db_connection()
        cursor = conn.cursor()
        
        q = self.mapper.get_query('selectInspStandardList', params)
        values = tuple(params.get(name) for name in q['params'])
        cursor.execute(q['query'], values)
        
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return rows

    def get_history(self, part_no, process_cd):
        params = {'part_no': part_no, 'process_cd': process_cd}
        conn = get_db_connection()
        cursor = conn.cursor()
        
        q = self.mapper.get_query('selectInspStandardHistory', params)
        values = tuple(params.get(name) for name in q['params'])
        cursor.execute(q['query'], values)
        
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return rows

    def get_details(self, code):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Master
        q_master = self.mapper.get_query('selectInspStandardByCode', {'CODE': code})
        cursor.execute(q_master['query'], (code,))
        col_m = [col[0] for col in cursor.description]
        row_m = dict(zip(col_m, cursor.fetchone())) if cursor.rowcount > 0 else None
        
        items = []
        if row_m:
            # Details
            q_item = self.mapper.get_query('selectInspStandardItem', {'PCODE': code})
            cursor.execute(q_item['query'], (code,))
            col_i = [col[0] for col in cursor.description]
            items = [dict(zip(col_i, row)) for row in cursor.fetchall()]
            
            # boolean conversion
            for item in items:
                item['CHOYN'] = bool(item.get('CHOYN'))
                item['SELFYN'] = bool(item.get('SELFYN'))
                
        conn.close()
        return {'master': row_m, 'items': items}

    def save(self, data: dict):
        """
        data = {
          "master": {
            "PLANTCD": "P001",
            "PARTNO": "P123",
            "PROCESSCD": "PRC01",
            "WDAY": "2026-04-20",
            "REVCONT": "Initial",
            "BIGO": ""
          },
          "items": [
            {
               "ITEMCODE": "I001", "ITEMSTEP": 1, "CHOYN": True, "SELFYN": False, ...
            }
          ]
        }
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            master = data.get('master', {})
            items = data.get('items', [])
            
            part_no = master.get('PARTNO')
            process_cd = master.get('PROCESSCD')
            
            if not part_no or not process_cd:
                raise ValueError("PARTNO and PROCESSCD are required")

            date_str = datetime.now().strftime("%Y%m%d")

            # 1. Get next REVNO
            q_rev = self.mapper.get_query('getMaxRevNo', {'PARTNO': part_no, 'PROCESSCD': process_cd})
            cursor.execute(q_rev['query'], (part_no, process_cd))
            max_rev = cursor.fetchone()[0]
            new_rev = max_rev + 1

            # 2. Get New Master Code
            q_code = self.mapper.get_query('getNewStandardCode', {'date_str': date_str})
            cursor.execute(q_code['query'], (date_str, date_str))
            new_code = cursor.fetchone()[0]

            # 3. Insert Master
            master_params = {
                'CODE': new_code,
                'REVCODE': f"{part_no}-{new_rev}",
                'PLANTCD': master.get('PLANTCD', 'P001'),
                'PARTNO': part_no,
                'PROCESSCD': process_cd,
                'WDAY': master.get('WDAY', datetime.now().strftime("%Y-%m-%d")),
                'REVNO': new_rev,
                'REVCONT': master.get('REVCONT', ''),
                'BIGO': master.get('BIGO', '')
            }
            
            q_ins_m = self.mapper.get_query('insertInspStandard', master_params)
            values_m = tuple(master_params.get(name) for name in q_ins_m['params'])
            cursor.execute(q_ins_m['query'], values_m)

            # 4. Insert Items
            for idx, item in enumerate(items):
                # Get New Item Code
                q_icode = self.mapper.get_query('getNewItemCode', {'date_str': date_str})
                cursor.execute(q_icode['query'], (date_str, date_str))
                new_icode = cursor.fetchone()[0]

                item_params = {
                    'CODE': new_icode,
                    'PCODE': new_code,
                    'ITEMCODE': item.get('ITEMCODE', ''),
                    'ITEMSTEP': item.get('ITEMSTEP') or (idx + 1),
                    'CHOYN': 1 if item.get('CHOYN') else 0,
                    'SELFYN': 1 if item.get('SELFYN') else 0,
                    'SAMPLEQTY': item.get('SAMPLEQTY', 0) or 0,
                    'PERIOD': item.get('PERIOD', ''),
                    'UNIT': item.get('UNIT', ''),
                    'OUTWARDVALUE': item.get('OUTWARDVALUE', ''),
                    'DIMSVALUE': item.get('DIMSVALUE') or None,
                    'PLUS': item.get('PLUS') or None,
                    'MINUS': item.get('MINUS') or None,
                    'BIGO': item.get('BIGO', '')
                }
                
                q_ins_i = self.mapper.get_query('insertInspStandardItem', item_params)
                values_i = tuple(item_params.get(name) for name in q_ins_i['params'])
                cursor.execute(q_ins_i['query'], values_i)

            conn.commit()
            return {"status": "success", "code": new_code, "rev_no": new_rev}
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

insp_standard_service = InspStandardService()
