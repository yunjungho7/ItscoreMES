from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from db.connection import get_db_connection, decode_cp949
from typing import Optional
from loguru import logger
from core.security import create_access_token, is_internal_ip
from core.email import generate_otp, send_otp_email, store_otp, verify_otp

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

class LoginRequest(BaseModel):
    empid: str
    password: str

class VerifyOTPRequest(BaseModel):
    empid: str
    otp: str

class UserInfo(BaseModel):
    empid: str
    name: str
    deptcd: Optional[str] = None
    plant: Optional[str] = None
    jikgub: Optional[str] = None
    email: Optional[str] = None

class LoginResponse(BaseModel):
    success: bool
    message: str
    status: str = "success"  # "success", "requires_2fa", "failed"
    access_token: Optional[str] = None
    user: Optional[UserInfo] = None

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, fastapi_request: Request):
    logger.info(f"Login attempt for user: {request.empid}")
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Check user credentials and status
        # Added EMAIL to the query
        query = """
            SELECT EMPID, NAME, DEPTCD, PLANT, JIKGUB, SHOWYN, RTRIM(EMAIL) as EMAIL
            FROM TBL_COM_MEMBERS 
            WHERE RTRIM(EMPID) = %s AND RTRIM(PASS) = %s
        """
        cursor.execute(query, (request.empid, request.password))
        row = cursor.fetchone()
        
        if not row:
            logger.warning(f"Login failed: user not found or password mismatch for {request.empid}")
            return LoginResponse(
                success=False,
                message="아이디 또는 비밀번호가 일치하지 않습니다.",
                status="failed"
            )
            
        # Decode fields
        empid = decode_cp949(row[0])
        name = decode_cp949(row[1])
        deptcd = decode_cp949(row[2])
        plant = decode_cp949(row[3])
        jikgub = decode_cp949(row[4])
        showyn = row[5]
        email = decode_cp949(row[6]) if row[6] else None
        
        logger.info(f"User found: {empid}, SHOWYN: {showyn}, Email: {email}")
        
        if not showyn:
            logger.warning(f"Login failed: account suspended for {empid}")
            return LoginResponse(
                success=False,
                message="사용이 중지된 계정입니다. 관리자에게 문의하세요.",
                status="failed"
            )

        user_info = UserInfo(
            empid=empid,
            name=name,
            deptcd=deptcd,
            plant=plant,
            jikgub=jikgub,
            email=email
        )
            
        # Check if internal IP
        internal = is_internal_ip(fastapi_request)
        
        if internal:
            logger.info(f"Internal access for {empid}, skipping 2FA")
            # Update last login time
            update_query = "UPDATE TBL_COM_MEMBERS SET LOGINYN = 'Y', LOGINDATE = GETDATE() WHERE EMPID = %s"
            cursor.execute(update_query, (empid,))
            conn.commit()
            
            token = create_access_token(data={"sub": empid, "name": name})
            
            return LoginResponse(
                success=True,
                message="로그인 성공",
                status="success",
                access_token=token,
                user=user_info
            )
        else:
            logger.info(f"External access for {empid}, requiring 2FA")
            if not email:
                return LoginResponse(
                    success=False,
                    message="등록된 이메일이 없어 2차 인증을 진행할 수 없습니다. 관리자에게 문의하세요.",
                    status="failed"
                )
            
            otp = generate_otp()
            store_otp(empid, otp)
            await send_otp_email(email, otp)
            
            return LoginResponse(
                success=True,
                message="2차 인증이 필요합니다. 이메일로 발송된 인증번호를 입력해 주세요.",
                status="requires_2fa",
                user=user_info # Return user info to client for context
            )
        
    except Exception as e:
        logger.error(f"Login exception for user {request.empid}: {str(e)}")
        if conn:
            conn.rollback()
        return LoginResponse(
            success=False,
            message=f"로그인 처리 중 오류 발생: {str(e)}",
            status="failed"
        )
    finally:
        if conn:
            conn.close()

@router.post("/verify-otp", response_model=LoginResponse)
def verify_otp_endpoint(request: VerifyOTPRequest):
    if verify_otp(request.empid, request.otp):
        logger.info(f"OTP verification successful for {request.empid}")
        
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            query = "SELECT EMPID, NAME, DEPTCD, PLANT, JIKGUB, RTRIM(EMAIL) as EMAIL FROM TBL_COM_MEMBERS WHERE EMPID = %s"
            cursor.execute(query, (request.empid,))
            row = cursor.fetchone()
            
            if not row:
                 raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
                 
            empid = decode_cp949(row[0])
            name = decode_cp949(row[1])
            
            # Update last login time
            update_query = "UPDATE TBL_COM_MEMBERS SET LOGINYN = 'Y', LOGINDATE = GETDATE() WHERE EMPID = %s"
            cursor.execute(update_query, (empid,))
            conn.commit()
            
            token = create_access_token(data={"sub": empid, "name": name})
            
            user_info = UserInfo(
                empid=empid,
                name=name,
                deptcd=decode_cp949(row[2]),
                plant=decode_cp949(row[3]),
                jikgub=decode_cp949(row[4]),
                email=decode_cp949(row[5]) if row[5] else None
            )
            
            return LoginResponse(
                success=True,
                message="인증 성공",
                status="success",
                access_token=token,
                user=user_info
            )
        finally:
            conn.close()
    else:
        logger.warning(f"OTP verification failed for {request.empid}")
        return LoginResponse(
            success=False,
            message="인증 번호가 일치하지 않거나 만료되었습니다.",
            status="failed"
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
