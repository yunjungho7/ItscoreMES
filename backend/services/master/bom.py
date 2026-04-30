"""BOM 서비스"""
from services.base_service import BaseCrudService

class BomService(BaseCrudService):
    def upsert_batch(self, data: dict):
        """
        BOM 일괄 저장 (Header-Detail 구조)
        - PAR_PARTNO 에 해당하는 기존 데이터를 모두 삭제 후 재등록
        """
        par_partno = data.get('PAR_PARTNO')
        details = data.get('details', [])
        reg_user_id = data.get('REGUSERID', 1)
        
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            
            # 1. 기존 데이터 삭제
            del_query = self.mapper.get_query('deleteByParent', {'PAR_PARTNO': par_partno})
            cursor.execute(del_query['query'], (par_partno,))
            
            # 2. 신규 데이터 등록
            ins_query = self.mapper.get_query('insert', {}) # Get parameter list structure
            for item in details:
                # Merge header and detail info
                row_data = {
                    'PAR_PARTNO': par_partno,
                    'CHILD_PARTNO': item.get('CHILD_PARTNO'),
                    'REQQTY': item.get('REQQTY', 0),
                    'ORD': item.get('ORD', 1),
                    'USEYN': True,
                    'REGUSERID': reg_user_id,
                    'EDITUSERID': reg_user_id
                }
                # Parameter names from the XML insert statement
                param_values = tuple(row_data.get(name) for name in ins_query['params'])
                cursor.execute(ins_query['query'], param_values)
            
            conn.commit()
            return {"statusCode": 201, "message": f"{len(details)}건의 BOM 정보가 저장되었습니다."}
        except Exception as e:
            conn.rollback()
            raise Exception(f"BOM 일괄 저장 중 오류 발생: {e}")
        finally:
            conn.close()

    def get_details(self, par_partno: str):
        """특정 모품목의 BOM 자식 목록 조회"""
        return self._execute_select('selectAll', {
            'search': par_partno,
            'offset': 0,
            'size': 9999
        })

    def get_where_used(self, child_partno: str):
        """특정 자식 품목을 사용하는 부모 품목 목록 조회 (역전개)"""
        return self._execute_select('selectWhereUsed', {
            'search': child_partno,
            'offset': 0,
            'size': 9999
        })

bom_service = BomService(
    mapper_path='sql/master/bom.xml',
    pk_columns=['PAR_PARTNO', 'CHILD_PARTNO']
)
