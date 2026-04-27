from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.connection import get_db_connection
from typing import Optional

router = APIRouter(
    prefix="/api/auth",
    tags=["Auth"]
)

class LoginRequest(BaseModel):
    empid: str
    password: str

class UserInfo(BaseModel):
    empid: str
    name: str
    deptcd: Optional[str] = None
    plant: str
    jikgub: Optional[str] = None

class LoginResponse(BaseModel):
    success: bool
    message: str
    user: Optional[UserInfo] = None

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Check user credentials and status
        query = """
            SELECT EMPID, NAME, DEPTCD, PLANT, JIKGUB, SHOWYN 
            FROM TBL_COM_MEMBERS 
            WHERE EMPID = %s AND PASS = %s
        """
        cursor.execute(query, (request.empid, request.password))
        row = cursor.fetchone()
        
        if not row:
            # Check if user exists but wrong password to give better error msg (optional)
            return LoginResponse(
                success=False,
                message="아이디 또는 비밀번호가 일치하지 않습니다."
            )
            
        empid, name, deptcd, plant, jikgub, showyn = row
        
        if not showyn:
            return LoginResponse(
                success=False,
                message="사용이 중지된 계정입니다. 관리자에게 문의하세요."
            )
            
        # Update last login time
        update_query = "UPDATE TBL_COM_MEMBERS SET LOGINYN = 'Y', LOGINDATE = GETDATE() WHERE EMPID = %s"
        cursor.execute(update_query, (empid,))
        conn.commit()
        
    finally:
        conn.close()
        
    return LoginResponse(
            success=True,
            message="로그인 성공",
            user=UserInfo(
                empid=empid,
                name=name,
                deptcd=deptcd,
                plant=plant,
                jikgub=jikgub
            )
        )

@router.post("/logout")
def logout(empid: str):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        update_query = "UPDATE TBL_COM_MEMBERS SET LOGINYN = 'N', LOGOUTDATE = GETDATE() WHERE EMPID = %s"
        cursor.execute(update_query, (empid,))
        conn.commit()
    finally:
        conn.close()
    return {"message": "로그아웃 성공"}
