from services.base_service import BaseService
from models.system.menu import MenuCreate, MenuUpdate
from fastapi import HTTPException
import os

class MenuService(BaseService):
    def __init__(self):
        super().__init__()
        # Load SQL XML for menu
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sql_path = os.path.join(current_dir, "..", "..", "sql", "system", "menu.xml")
        from db.xml_mapper import XMLMapper
        self.sql_mapper = XMLMapper(sql_path)

    def get_menus(self):
        query_info = self.sql_mapper.get_query("selectList", {})
        return self.execute_query(query_info, {})

    def create_menu(self, menu: MenuCreate):
        # 중복 체크
        check_query = "SELECT COUNT(*) as cnt FROM TBL_COM_MENU WHERE MENUCD = %s"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(check_query, (menu.MENUCD,))
            row = cursor.fetchone()
            if row and row[0] > 0:
                raise HTTPException(status_code=400, detail="이미 존재하는 메뉴코드입니다.")

        menu_dict = menu.model_dump()
        menu_dict["SEARCH"] = 1 if menu_dict.get("SEARCH") else 0
        menu_dict["REGEDIT"] = 1 if menu_dict.get("REGEDIT") else 0
        menu_dict["USE_YN"] = 1 if menu_dict.get("USE_YN") else 0
        
        # PAR_MENUCD가 빈 문자열인 경우 None으로 처리
        if not menu_dict.get("PAR_MENUCD"):
            menu_dict["PAR_MENUCD"] = None

        query_info = self.sql_mapper.get_query("insert", menu_dict)
        return self.execute_query(query_info, menu_dict)

    def update_menu(self, menucd: str, menu: MenuUpdate):
        menu_dict = menu.model_dump()
        menu_dict["MENUCD"] = menucd
        menu_dict["SEARCH"] = 1 if menu_dict.get("SEARCH") else 0
        menu_dict["REGEDIT"] = 1 if menu_dict.get("REGEDIT") else 0
        menu_dict["USE_YN"] = 1 if menu_dict.get("USE_YN") else 0

        # PAR_MENUCD가 빈 문자열인 경우 None으로 처리
        if not menu_dict.get("PAR_MENUCD"):
            menu_dict["PAR_MENUCD"] = None

        query_info = self.sql_mapper.get_query("update", menu_dict)
        row_count = self.execute_query(query_info, menu_dict)
        
        if row_count == 0:
            raise HTTPException(status_code=404, detail="메뉴를 찾을 수 없거나 업데이트된 내용이 없습니다.")
            
        return row_count

    def delete_menu(self, menucd: str):
        params = {"MENUCD": menucd}
        
        # 하위 메뉴 존재 여부 체크 (선택적)
        check_query = "SELECT COUNT(*) as cnt FROM TBL_COM_MENU WHERE PAR_MENUCD = %s"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(check_query, (menucd,))
            row = cursor.fetchone()
            if row and row[0] > 0:
                raise HTTPException(status_code=400, detail="하위 메뉴가 존재하여 삭제할 수 없습니다.")

        query_info = self.sql_mapper.get_query("delete", params)
        row_count = self.execute_query(query_info, params)
        
        if row_count == 0:
            raise HTTPException(status_code=404, detail="메뉴를 찾을 수 없습니다.")
            
        return row_count
