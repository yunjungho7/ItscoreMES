from services.base_service import BaseService
from models.system.user import UserCreate, UserUpdate
from fastapi import HTTPException
import os

class UserService(BaseService):
    def __init__(self):
        super().__init__()
        # Get absolute path to the sql file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sql_path = os.path.join(current_dir, "..", "..", "sql", "system", "user.xml")
        from db.xml_mapper import XMLMapper
        self.sql_mapper = XMLMapper(sql_path)

    def get_users(self, plant: str = None, name: str = None, deptcd: str = None, showyn: bool = None):
        params = {}
        if plant:
            params['PLANT'] = plant
        if name:
            params['NAME'] = name
        if deptcd:
            params['DEPTCD'] = deptcd
        if showyn is not None:
            params['SHOWYN'] = 1 if showyn else 0

        query_info = self.sql_mapper.get_query("selectList", params)
        results = self.execute_query(query_info, params)
        # 프론트엔드 일관성을 위해 키를 대문자로 변환
        return [{k.upper(): v for k, v in row.items()} for row in results] if isinstance(results, list) else results

    def create_user(self, user: UserCreate):
        # 1. 중복 체크
        check_params = {"EMPID": user.EMPID}
        check_query = "SELECT COUNT(*) as cnt FROM TBL_COM_MEMBERS WHERE EMPID = %s"
        
        # BaseService의 connection을 사용하여 직접 쿼리 실행
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(check_query, (user.EMPID,))
            row = cursor.fetchone()
            if row and row[0] > 0:
                raise HTTPException(status_code=400, detail="이미 존재하는 사번입니다.")

        # 2. 저장
        user_dict = user.model_dump()
        user_dict["SHOWYN"] = 1 if user_dict.get("SHOWYN") else 0
        
        query_info = self.sql_mapper.get_query("insert", user_dict)
        return self.execute_query(query_info, user_dict)

    def update_user(self, empid: str, user: UserUpdate):
        user_dict = user.model_dump()
        user_dict["EMPID"] = empid
        user_dict["SHOWYN"] = 1 if user_dict.get("SHOWYN") else 0
        
        query_info = self.sql_mapper.get_query("update", user_dict)
        row_count = self.execute_query(query_info, user_dict)
        
        if row_count == 0:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없거나 업데이트된 내용이 없습니다.")
            
        return row_count

    def delete_user(self, empid: str):
        params = {"EMPID": empid}
        query_info = self.sql_mapper.get_query("delete", params)
        row_count = self.execute_query(query_info, params)
        
        if row_count == 0:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
            
        return row_count
