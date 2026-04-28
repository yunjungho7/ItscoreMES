"""
공통 CRUD 서비스 (MyBatis XML Mapper 기반)
- XML 파일에서 쿼리를 로드하여 실행
- 동적 SQL 조건(if/where/set) 지원
"""
import pymssql
import os
from db.connection import get_db_connection, execute_query
from db.xml_mapper import XMLMapper
from typing import Optional

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
    def __init__(self, mapper_path: str, pk_columns: list):
        """
        mapper_path: XML 파일 경로 (backend/ 기준 상대경로, 예: 'sql/master/plant.xml')
        pk_columns: PK 컬럼 목록 (예: ['PLANTCD'])
        """
        xml_full_path = os.path.join(BASE_DIR, mapper_path)
        self.mapper = XMLMapper(xml_full_path)
        self.pk_columns = pk_columns

    def _get_conn(self):
        return get_db_connection()

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
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
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
            raise Exception(f"데이터 무결성 오류: {e}")
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

        items = self._execute_select('get_list', params)
        total = self._execute_scalar('get_count', params)

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
        items = self._execute_select('get_one', pks)
        return items[0] if items else None

    def create(self, data: dict):
        """등록"""
        return self._execute_update('insert', data)

    def update(self, data: dict):
        """수정"""
        return self._execute_update('update', data)

    def delete(self, **pks):
        """삭제"""
        return self._execute_update('delete', pks)

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