from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.connection import get_db_connection, decode_cp949
from typing import Optional
from loguru import logger

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

class LoginRequest(BaseModel):
    empid: str
    password: str

class UserInfo(BaseModel):
    empid: str
    name: str
    deptcd: Optional[str] = None
    plant: Optional[str] = None
    jikgub: Optional[str] = None

class LoginResponse(BaseModel):
    success: bool
    message: str
    user: Optional[UserInfo] = None

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    logger.info(f"Login attempt for user: {request.empid}")
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Check user credentials and status
        # Use RTRIM for EMPID and PASS to handle CHAR columns with trailing spaces
        query = """
            SELECT EMPID, NAME, DEPTCD, PLANT, JIKGUB, SHOWYN 
            FROM TBL_COM_MEMBERS 
            WHERE RTRIM(EMPID) = %s AND RTRIM(PASS) = %s
        """
        cursor.execute(query, (request.empid, request.password))
        row = cursor.fetchone()
        
        if not row:
            logger.warning(f"Login failed: user not found or password mismatch for {request.empid}")
            return LoginResponse(
                success=False,
                message="아이디 또는 비밀번호가 일치하지 않습니다."
            )
            
        # Decode fields
        empid = decode_cp949(row[0])
        name = decode_cp949(row[1])
        deptcd = decode_cp949(row[2])
        plant = decode_cp949(row[3])
        jikgub = decode_cp949(row[4])
        showyn = row[5]
        
        logger.info(f"User found: {empid}, SHOWYN: {showyn}")
        
        if not showyn:
            logger.warning(f"Login failed: account suspended for {empid}")
            return LoginResponse(
                success=False,
                message="사용이 중지된 계정입니다. 관리자에게 문의하세요."
            )
            
        # Update last login time
        update_query = "UPDATE TBL_COM_MEMBERS SET LOGINYN = 'Y', LOGINDATE = GETDATE() WHERE EMPID = %s"
        cursor.execute(update_query, (empid,))
        conn.commit()
        
        logger.info(f"Login successful for user: {empid}")
        
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
        
    except Exception as e:
        logger.error(f"Login exception for user {request.empid}: {str(e)}")
        if conn:
            conn.rollback()
        return LoginResponse(
            success=False,
            message=f"로그인 처리 중 오류 발생: {str(e)}"
        )
    finally:
        if conn:
            conn.close()

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
