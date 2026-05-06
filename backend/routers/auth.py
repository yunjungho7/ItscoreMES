from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from db.connection import get_db_connection, decode_cp949
from core.security import create_access_token
from core.email import send_otp_email
from core.config import settings
from datetime import datetime, timedelta
import random
import string
import uuid
from typing import Optional, Dict

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

# Temporary in-memory store for OTPs (In production, use Redis or DB)
# format: {session_id: {"empid": str, "otp": str, "expires": datetime, "user_info": dict}}
otp_store: Dict[str, dict] = {}

class LoginRequest(BaseModel):
    empid: str
    password: str

class OTPVerifyRequest(BaseModel):
    session_id: str
    otp_code: str

class UserInfo(BaseModel):
    empid: str
    name: str
    deptcd: Optional[str] = None
    plant: str
    jikgub: Optional[str] = None

class LoginResponse(BaseModel):
    success: bool
    message: str
    requires_2fa: bool = False
    session_id: Optional[str] = None
    access_token: Optional[str] = None
    token_type: Optional[str] = "bearer"
    user: Optional[UserInfo] = None

def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, background_tasks: BackgroundTasks):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Check user credentials and status
        query = """
            SELECT EMPID, NAME, DEPTCD, PLANT, JIKGUB, SHOWYN, EMAIL 
            FROM TBL_COM_MEMBERS 
            WHERE EMPID = %s AND RTRIM(PASS) = %s
        """
        cursor.execute(query, (request.empid, request.password))
        row = cursor.fetchone()
        
        if not row:
            return LoginResponse(
                success=False,
                message="아이디 또는 비밀번호가 일치하지 않습니다."
            )
            
        empid = decode_cp949(row[0])
        name = decode_cp949(row[1])
        deptcd = decode_cp949(row[2])
        plant = decode_cp949(row[3])
        jikgub = decode_cp949(row[4])
        showyn = row[5]
        email = decode_cp949(row[6]) if row[6] else None
        
        if not showyn:
            return LoginResponse(
                success=False,
                message="사용이 중지된 계정입니다. 관리자에게 문의하세요."
            )
            
        if not email:
             return LoginResponse(
                success=False,
                message="등록된 이메일 주소가 없습니다. 관리자에게 문의하세요."
            )

        # 1. Generate OTP and Session ID
        otp_code = generate_otp()
        session_id = str(uuid.uuid4())
        expires = datetime.now() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
        
        user_info = UserInfo(
            empid=empid,
            name=name,
            deptcd=deptcd,
            plant=plant,
            jikgub=jikgub
        )

        # 2. Store OTP info
        otp_store[session_id] = {
            "empid": empid,
            "otp": otp_code,
            "expires": expires,
            "user_info": user_info
        }

        # 3. Send Email in Background
        background_tasks.add_task(send_otp_email, email, otp_code)
        
        return LoginResponse(
            success=True,
            message="인증 번호가 메일로 발송되었습니다.",
            requires_2fa=True,
            session_id=session_id
        )
        
    finally:
        conn.close()

@router.post("/verify-otp", response_model=LoginResponse)
def verify_otp(request: OTPVerifyRequest):
    session_data = otp_store.get(request.session_id)
    
    if not session_data:
        raise HTTPException(status_code=400, detail="유효하지 않은 세션입니다.")
    
    if datetime.now() > session_data["expires"]:
        del otp_store[request.session_id]
        raise HTTPException(status_code=400, detail="인증 번호가 만료되었습니다.")
    
    if session_data["otp"] != request.otp_code:
        return LoginResponse(
            success=False,
            message="인증 번호가 일치하지 않습니다."
        )

    # Success! Issue JWT
    empid = session_data["empid"]
    user_info = session_data["user_info"]
    access_token = create_access_token(subject=empid)
    
    # Cleanup OTP store
    del otp_store[request.session_id]
    
    # Update last login time in DB
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        update_query = "UPDATE TBL_COM_MEMBERS SET LOGINYN = 'Y', LOGINDATE = GETDATE() WHERE EMPID = %s"
        cursor.execute(update_query, (empid,))
        conn.commit()
    finally:
        conn.close()

    return LoginResponse(
        success=True,
        message="로그인 성공",
        access_token=access_token,
        user=user_info
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
