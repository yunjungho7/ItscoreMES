"""입고관리 서비스"""
from db.xml_mapper import XMLMapper
from db.connection import get_db_connection
import math
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ReceiveService:
    def __init__(self):
        self.mapper = XMLMapper(os.path.join(BASE_DIR, 'sql/logistics/receive.xml'))

    def get_all(self, start_date=None, end_date=None, plant_cd=None, company_cd=None, order_num=None, search=None, page=1, size=50):
        params = {}
        if start_date: params['start_date'] = start_date
        if end_date: params['end_date'] = end_date
        if plant_cd: params['plant_cd'] = plant_cd
        if company_cd: params['company_cd'] = company_cd
        if order_num: params['order_num'] = order_num
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
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return {"data": rows, "total": total, "page": page, "totalPages": math.ceil(total / size) if total else 0}

    def get_details(self, warehouse_num):
        params = {'WAREHOUSENUM': warehouse_num}
        q = self.mapper.get_query('selectDetails', params)
        values = tuple(params.get(name) for name in q['params'])
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(q['query'], values)
        columns = [col[0].upper() for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return rows

    def get_next_num(self):
        q = self.mapper.get_query('selectNextNum', {})
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(q['query'])
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else 'WH00000000-001'

    def create(self, data: dict):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # 1. WAREHOUSENUM 채번 (Transaction 내에서 UPDLOCK 사용)
            q_num = self.mapper.get_query('selectNextNum', {})
            cursor.execute(q_num['query'])
            row_num = cursor.fetchone()
            wh_num = row_num[0] if row_num else 'WH' + datetime.datetime.now().strftime('%Y%m%d') + '-001'
            
            details = data.pop('details', [])
            data['WAREHOUSENUM'] = wh_num
            data['WHSTATE'] = 'RECEIVED'
            data['INTIME'] = ''
            
            # 필수 필드 기본값 보장
            if not data.get('INGUBUN'):
                data['INGUBUN'] = 'PURCHASE'
            if not data.get('REGUSERID'):
                data['REGUSERID'] = '1'

            order_num = data.get('ORDERNUM') or data.get('order_num') or ''

            # 2. 헤더 저장
            q_ins = self.mapper.get_query('insert', data)
            cursor.execute(q_ins['query'], tuple(data.get(name) for name in q_ins['params']))

            # 3. LOT 번호 채번 (UPDLOCK)
            import datetime
            lot_q = self.mapper.get_query('selectNextLotNo', {})
            cursor.execute(lot_q['query'])
            lot_row = cursor.fetchone()
            base_lot_no = lot_row[0] if lot_row else f"L{datetime.datetime.now().strftime('%y%m%d')}001"
            
            if len(base_lot_no) >= 10:
                lot_seq = int(base_lot_no[-3:])
                lot_prefix = base_lot_no[:-3]
            else:
                lot_seq = 1
                lot_prefix = f"L{datetime.datetime.now().strftime('%y%m%d')}"

            # 4. 상세 저장 및 재고 반영
            for i, d in enumerate(details):
                d['WAREHOUSENUM'] = wh_num
                d['WHDETAILNO'] = i + 1
                d['INDAY'] = data.get('INDAY')
                if not d.get('LOTNO'):
                    current_seq = lot_seq + i
                    d['LOTNO'] = f"{lot_prefix}{current_seq:03d}"
                
                if not d.get('LOCATIONCODE'): d['LOCATIONCODE'] = 'LOC001'
                if not d.get('WAREHOUSECODE'): d['WAREHOUSECODE'] = 'WH001'

                inlotqty = d.get('INLOTQTY') or d.get('ORDERQTY') or 0
                d['INLOTQTY'] = inlotqty

                dq = self.mapper.get_query('insertDetail', d)
                cursor.execute(dq['query'], tuple(d.get(name) for name in dq['params']))

                # Lot State & Stock
                lot_data = {
                    'LOTNO': d['LOTNO'], 'PARTNO': d['PARTNO'], 'LOTQTY': inlotqty,
                    'WAREHOUSECODE': d['WAREHOUSECODE'], 'LOCATIONCODE': d['LOCATIONCODE'],
                    'LOTCREATIONDAY': d['INDAY'], 'LOTTYPE': 'PURCHASE', 'REMARK': '입고완료(발주)'
                }
                
                lq = self.mapper.get_query('insertLotState', lot_data)
                if lq: cursor.execute(lq['query'], tuple(lot_data.get(name) for name in lq['params']))

                sq = self.mapper.get_query('insertStock', lot_data)
                if sq: cursor.execute(sq['query'], tuple(lot_data.get(name) for name in sq['params']))

                # Update PO detail
                if order_num:
                    up_params = {'ORDERNUM': order_num, 'PARTNO': d['PARTNO'], 'INLOTQTY': inlotqty}
                    up_q = self.mapper.get_query('updatePurchaseOrderDetailInQty', up_params)
                    if up_q: cursor.execute(up_q['query'], tuple(up_params.get(n) for n in up_q['params']))

            # 5. PO 상태 업데이트
            if order_num:
                remain_q = self.mapper.get_query('selectPurchaseOrderRemainCount', {'ORDERNUM': order_num})
                cursor.execute(remain_q['query'], (order_num,))
                remain_row = cursor.fetchone()
                new_state = 'COMPLETED' if (remain_row[0] if remain_row else 0) == 0 else 'PARTIAL'
                
                uq = self.mapper.get_query('updatePurchaseOrderState', {'ORDERNUM': order_num, 'ORDERSTATE': new_state})
                cursor.execute(uq['query'], (new_state, order_num))

            conn.commit()
            return {"WAREHOUSENUM": wh_num}
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def delete(self, warehouse_num):
        """입고 취소: LOT/재고 삭제, 발주 입고수량 복원, 발주 상태 재계산"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # 1. 입고 헤더 조회 (ORDERNUM 확인)
            hdr_q = self.mapper.get_query('selectWarehouseHeader', {'WAREHOUSENUM': warehouse_num})
            cursor.execute(hdr_q['query'], tuple({'WAREHOUSENUM': warehouse_num}.get(n) for n in hdr_q['params']))
            hdr_cols = [col[0] for col in cursor.description]
            hdr_row = cursor.fetchone()
            if not hdr_row:
                return False
            header = dict(zip(hdr_cols, hdr_row))
            order_num = header.get('ORDERNUM') or ''

            # 2. 입고 상세 목록 조회
            det_q = self.mapper.get_query('selectCancelDetails', {'WAREHOUSENUM': warehouse_num})
            cursor.execute(det_q['query'], tuple({'WAREHOUSENUM': warehouse_num}.get(n) for n in det_q['params']))
            det_cols = [col[0] for col in cursor.description]
            details = [dict(zip(det_cols, r)) for r in cursor.fetchall()]

            # 3. 각 상세 행별 LOT/재고 삭제 및 발주 INQTY 복원
            for d in details:
                lot_no = d.get('LOTNO')
                if lot_no:
                    # 재고 삭제
                    sq = self.mapper.get_query('deleteStock', {'LOTNO': lot_no})
                    if sq:
                        cursor.execute(sq['query'], tuple({'LOTNO': lot_no}.get(n) for n in sq['params']))
                    # LOT 상태 삭제
                    lq = self.mapper.get_query('deleteLotState', {'LOTNO': lot_no})
                    if lq:
                        cursor.execute(lq['query'], tuple({'LOTNO': lot_no}.get(n) for n in lq['params']))

                # 발주 기반이면 INQTY 차감 복원
                if order_num:
                    rv_params = {
                        'ORDERNUM': order_num,
                        'PARTNO': d['PARTNO'],
                        'INLOTQTY': d.get('INLOTQTY') or 0
                    }
                    rv_q = self.mapper.get_query('revertPurchaseOrderDetailInQty', rv_params)
                    if rv_q:
                        cursor.execute(rv_q['query'], tuple(rv_params.get(n) for n in rv_q['params']))

            # 4. 입고 상세 soft delete
            sd_q = self.mapper.get_query('softDeleteDetails', {'WAREHOUSENUM': warehouse_num})
            if sd_q:
                cursor.execute(sd_q['query'], tuple({'WAREHOUSENUM': warehouse_num}.get(n) for n in sd_q['params']))

            # 5. 입고 헤더 soft delete
            params = {'WAREHOUSENUM': warehouse_num, 'EDITUSERID': '1'}
            q = self.mapper.get_query('softDelete', params)
            cursor.execute(q['query'], tuple(params.get(name) for name in q['params']))

            # 6. 발주 상태 재계산
            if order_num:
                remain_q = self.mapper.get_query('selectPurchaseOrderRemainCount', {'ORDERNUM': order_num})
                if remain_q:
                    cursor.execute(remain_q['query'], tuple({'ORDERNUM': order_num}.get(n) for n in remain_q['params']))
                    remain_row = cursor.fetchone()
                    remain_cnt = remain_row[0] if remain_row else 0

                    # 전체 품목 수 조회해서 전부 미입고면 ORDERED, 일부면 PARTIAL
                    # remain_cnt = 미입고 건수이므로, 총 건수와 비교
                    # 간단히: 전부 미입고 → ORDERED, 일부 입고 → PARTIAL, 전부 입고 → COMPLETED
                    if remain_cnt == 0:
                        new_state = 'COMPLETED'
                    else:
                        # 모든 품목이 INQTY=0인지 확인 → 전부 미입고면 ORDERED
                        chk_q = self.mapper.get_query('selectPurchaseOrderRemainCount', {'ORDERNUM': order_num})
                        # remain_cnt > 0 이면 미입고 잔여가 있음
                        # 추가로 일부라도 입고되었는지 확인
                        new_state = 'ORDERED'
                        # PARTIAL인지 확인: INQTY > 0인 항목이 하나라도 있으면 PARTIAL
                        cursor.execute(
                            "SELECT COUNT(*) FROM TBL_INOUT_PURCHASE_ORDER_DETAIL WHERE ORDERNUM = %s AND USEYN = 1 AND ISNULL(INQTY, 0) > 0",
                            (order_num,)
                        )
                        has_in = cursor.fetchone()[0]
                        if has_in > 0:
                            new_state = 'PARTIAL'

                    uq = self.mapper.get_query('updatePurchaseOrderState', {'ORDERNUM': order_num, 'ORDERSTATE': new_state})
                    if uq:
                        cursor.execute(uq['query'], tuple({'ORDERNUM': order_num, 'ORDERSTATE': new_state}.get(name) for name in uq['params']))

            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_summary(self):
        q = self.mapper.get_query('selectSummary', {})
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(q['query'])
        columns = [col[0] for col in cursor.description]
        row = cursor.fetchone()
        res = dict(zip(columns, row)) if row else {"expected_today": 0, "in_progress": 0, "quality_pending": 0}
        conn.close()
        return res


receive_service = ReceiveService()
