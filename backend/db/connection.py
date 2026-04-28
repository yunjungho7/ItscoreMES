import pymssql
from sqlalchemy import create_engine, String, TypeDecorator
from sqlalchemy.orm import sessionmaker
from backend.core.config import settings

class CP949String(TypeDecorator):
    """
    Centralized CP949 decoding logic for SQLAlchemy.
    Converts latin-1 (how pymssql often returns CP949 bytes) to cp949 and then to utf-8.
    """
    impl = String
    cache_ok = True

    def process_result_value(self, value, dialect):
        if value is not None and isinstance(value, str):
            try:
                return value.encode('latin-1').decode('cp949')
            except (UnicodeEncodeError, UnicodeDecodeError):
                return value
        return value

def decode_cp949(value):
    """Helper for manual decoding consistency"""
    if value is not None and isinstance(value, str):
        try:
            return value.encode('latin-1').decode('cp949')
        except (UnicodeEncodeError, UnicodeDecodeError):
            return value
    return value

def db_creator():
    last_error = None
    for server in settings.DB_SERVERS:
        try:
            conn = pymssql.connect(
                server=server,
                user=settings.DB_UID,
                password=settings.DB_PWD,
                database=settings.DB_NAME,
                charset='utf8',
                login_timeout=2
            )
            return conn
        except Exception as e:
            last_error = e
            continue
    
    raise Exception(f"모든 Database 서버({', '.join(settings.DB_SERVERS)}) 연결 실패: {last_error}")

# SQLAlchemy Engine with Connection Pooling and Multi-IP Failover
engine = create_engine(
    "mssql+pymssql://",
    creator=db_creator,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_session():
    """FastAPI Dependency for DB Session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_connection():
    """
    Returns a raw connection from the pool.
    Maintained for backward compatibility.
    """
    return engine.raw_connection()

def execute_query(conn, query_info, param_dict=None):
    """
    conn: DB Connection 객체 (raw pymssql connection or proxy)
    query_info: XMLMapper 에서 반환된 {query: '...', params: ['...']}
    param_dict: 실제 값이 담긴 딕셔너리 (예: {"user_id": 1})
    """
    if param_dict is None:
        param_dict = {}
        
    cursor = conn.cursor()
    query = query_info['query']
    param_names = query_info['params']
    
    # XML 쿼리의 #{param} 순서에 맞게 값을 배열로 변환
    values = tuple(param_dict.get(name) for name in param_names)
    
    try:
        cursor.execute(query, values)
        
        # SELECT 문인 경우 결과를 Dictionary 리스트로 변환하여 반환
        if query.strip().upper().startswith("SELECT"):
            columns = [column[0] for column in cursor.description]
            results = []
            for row in cursor.fetchall():
                row_dict = {}
                for i, value in enumerate(row):
                    # Use centralized decoding
                    row_dict[columns[i]] = decode_cp949(value)
                results.append(row_dict)
            return results
        else:
            conn.commit()
            return cursor.rowcount
    except Exception as e:
        if hasattr(conn, 'rollback'):
            conn.rollback()
        raise e
    finally:
        cursor.close()
