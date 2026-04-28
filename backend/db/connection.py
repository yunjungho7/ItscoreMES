import pymssql
import os

# 환경 변수나 설정 파일에서 가져오는 것이 좋으나, 
# 사용자로부터 DB 정보를 받지 않았으므로 로컬 기본값을 세팅해 둡니다.
# 여러 개의 DB 서버 IP를 정의 (우선순위 순서)
DB_SERVERS = ["192.168.0.5", "192.168.1.5"]
DB_NAME = os.getenv("DB_NAME", "PFMES")
DB_UID = os.getenv("DB_UID", "SA")
DB_PWD = os.getenv("DB_PWD", "itscore1!")

def get_db_connection():
    last_error = None
    for server in DB_SERVERS:
        try:
            conn = pymssql.connect(
                server=server,
                user=DB_UID,
                password=DB_PWD,
                database=DB_NAME,
                charset='utf8',
                login_timeout=2  # 빠른 타임아웃 설정을 통해 다음 IP 시도
            )
            return conn
        except Exception as e:
            last_error = e
            continue
    
    raise Exception(f"모든 Database 서버({', '.join(DB_SERVERS)}) 연결 실패: {last_error}")

def execute_query(conn, query_info, param_dict=None):
    """
    conn: DB Connection 객체
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
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return results
        else:
            conn.commit()
            return cursor.rowcount
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
