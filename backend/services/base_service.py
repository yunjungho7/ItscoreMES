"""
공통 CRUD 서비스 (MyBatis XML Mapper 기반)
- XML 파일에서 쿼리를 로드하여 실행
- 동적 SQL 조건(if/where/set) 지원
"""
import pymssql
import os
from db.connection import get_db_connection, execute_query, decode_cp949
from db.xml_mapper import XMLMapper
from typing import Optional
from fastapi import HTTPException

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class BaseService:
    def __init__(self):
        pass

    def get_connection(self):
        return get_db_connection()

    def execute_query(self, query_info, params=None):
        conn = self.get_connection()
        try:
            return execute_query(conn, query_info, params)
        finally:
            conn.close()


class BaseCrudService:
    def __init__(self, mapper_path: str, pk_columns: list, table_name: str = None):
        """
        mapper_path: XML 파일 경로 (backend/ 기준 상대경로, 예: 'sql/master/plant.xml')
        pk_columns: PK 컬럼 목록 (예: ['PLANTCD'])
        table_name: 감사 로그용 테이블명 (예: 'TBL_COM_PLANT')
        """
        xml_full_path = os.path.join(BASE_DIR, mapper_path)
        self.mapper = XMLMapper(xml_full_path)
        self.pk_columns = pk_columns
        self.table_name = table_name

    def _get_conn(self):
        return get_db_connection()

    def _record_audit(self, cursor, action: str, pk_val: str, user_id: str):
        """감사 로그 기록 (공통)"""
        if not self.table_name:
            return
        
        sql = """
            INSERT INTO TBL_SYS_AUDIT_LOG (TABLE_NAME, ACTION_TYPE, TARGET_PK, USER_ID, LOG_DTM)
            VALUES (%s, %s, %s, %s, GETDATE())
        """
        cursor.execute(sql, (self.table_name, action, str(pk_val), str(user_id)))

    def get_query(self, query_id, params=None):
        return self.mapper.get_query(query_id, params)

    def _execute_select(self, query_id, params=None):
        """SELECT 실행 후 Dictionary 리스트 반환"""
        query_info = self.mapper.get_query(query_id, params)
        if not query_info:
            return []

        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            values = tuple(
                params.get(name) for name in query_info['params']
            ) if params else ()
            cursor.execute(query_info['query'], values)
            # 컬럼명을 항상 대문자로 변환하여 프론트엔드와 일치시킴
            columns = [column[0].upper() for column in cursor.description]
            results = []
            for row in cursor.fetchall():
                row_dict = {}
                for i, value in enumerate(row):
                    row_dict[columns[i]] = decode_cp949(value)
                results.append(row_dict)
            
            print(f"DEBUG [{query_id}]: {len(results)} rows fetched.")
            return results
        finally:
            conn.close()

    def _execute_scalar(self, query_id, params=None):
        """단일 값 반환 (COUNT 등)"""
        query_info = self.mapper.get_query(query_id, params)
        if not query_info:
            return 0
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            values = tuple(
                params.get(name) for name in query_info['params']
            ) if params else ()
            cursor.execute(query_info['query'], values)
            row = cursor.fetchone()
            return row[0] if row else 0
        finally:
            conn.close()

    def _execute_update(self, query_id, params=None):
        """INSERT/UPDATE/DELETE 실행 후 영향받은 행 수 반환"""
        query_info = self.mapper.get_query(query_id, params)
        if not query_info:
            raise Exception(f"Query '{query_id}' not found")
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            values = tuple(
                params.get(name) for name in query_info['params']
            ) if params else ()
            cursor.execute(query_info['query'], values)
            conn.commit()
            return cursor.rowcount
        except pymssql.IntegrityError as e:
            conn.rollback()
            # SQL Server Foreign Key violation error code is usually 547
            error_msg = str(e)
            if "547" in error_msg:
                raise HTTPException(status_code=400, detail="참조 무결성 오류: 관련 데이터가 존재하지 않거나 참조 중입니다.")
            raise HTTPException(status_code=400, detail=f"데이터 무결성 오류: {e}")
        finally:
            conn.close()

    # ── 공통 CRUD 메서드 ──

    def get_all(self, search: Optional[str] = None,
                page: int = 1, size: int = 50, **extra_params) -> dict:
        """목록 조회 (검색 + 페이징)"""
        params = {
            'offset': (page - 1) * size,
            'size': size,
        }
        if search:
            params['search'] = f"%{search}%"

        params.update(extra_params)

        items = self._execute_select('selectAll', params)
        total = self._execute_scalar('countAll', params)

        total_pages = (total + size - 1) // size if size > 0 else 1
        return {
            "data": items,
            "total": total,
            "page": page,
            "size": size,
            "totalPages": total_pages
        }

    def get_one(self, **pks) -> Optional[dict]:
        """단건 조회"""
        items = self._execute_select('selectById', pks)
        return items[0] if items else None

    def get_by_id(self, pks: dict) -> Optional[dict]:
        """ID로 조회 (Alias for get_one)"""
        return self.get_one(**pks)

    def create(self, data: dict):
        """등록 (감사 로그 포함)"""
        def callback(cursor):
            query_info = self.mapper.get_query('insert', data)
            values = tuple(data.get(name) for name in query_info['params'])
            cursor.execute(query_info['query'], values)
            
            # PK 값 추출 (복합 PK 지원)
            pk_val = "-".join([str(data.get(c, '')) for c in self.pk_columns])
            user_id = data.get('REGUSERID', data.get('USER_ID', '1'))
            self._record_audit(cursor, 'INSERT', pk_val, user_id)
            return cursor.rowcount
        
        try:
            return self._execute_transaction(callback)
        except pymssql.IntegrityError as e:
            error_msg = str(e)
            if "547" in error_msg:
                raise HTTPException(status_code=400, detail="참조 무결성 오류: 관련 데이터가 존재하지 않거나 참조 중입니다.")
            raise HTTPException(status_code=400, detail=f"데이터 무결성 오류: {e}")

    def update(self, pks: dict, data: dict):
        """수정 (감사 로그 포함)"""
        params = {**pks, **data}
        def callback(cursor):
            query_info = self.mapper.get_query('update', params)
            values = tuple(params.get(name) for name in query_info['params'])
            cursor.execute(query_info['query'], values)
            
            pk_val = "-".join([str(pks.get(c, '')) for c in self.pk_columns])
            user_id = params.get('EDITUSERID', params.get('USER_ID', '1'))
            self._record_audit(cursor, 'UPDATE', pk_val, user_id)
            return cursor.rowcount
        
        try:
            return self._execute_transaction(callback)
        except pymssql.IntegrityError as e:
            error_msg = str(e)
            if "547" in error_msg:
                raise HTTPException(status_code=400, detail="참조 무결성 오류: 관련 데이터가 존재하지 않거나 참조 중입니다.")
            raise HTTPException(status_code=400, detail=f"데이터 무결성 오류: {e}")

    def delete(self, pks: dict):
        """삭제 (감사 로그 포함)"""
        def callback(cursor):
            query_info = self.mapper.get_query('softDelete', pks)
            values = tuple(pks.get(name) for name in query_info['params'])
            cursor.execute(query_info['query'], values)
            
            pk_val = "-".join([str(pks.get(c, '')) for c in self.pk_columns])
            user_id = pks.get('EDITUSERID', pks.get('USER_ID', '1'))
            self._record_audit(cursor, 'DELETE', pk_val, user_id)
            return cursor.rowcount
        
        return self._execute_transaction(callback)

    def _execute_transaction(self, callback):
        """트랜잭션 실행 (callback 에 cursor 전달)"""
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            result = callback(cursor)
            conn.commit()
            return result
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()