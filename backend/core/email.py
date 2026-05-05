import random
import string
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from core.config import settings
from cachetools import TTLCache
from typing import Optional
from loguru import logger

# In-memory cache for OTP codes (Expires in 5 minutes)
otp_cache = TTLCache(maxsize=1000, ttl=300)

conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.SMTP_FROM_EMAIL,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

def generate_otp(length: int = 6) -> str:
    return ''.join(random.choices(string.digits, k=length))

async def send_otp_email(email: str, otp: str):
    message = MessageSchema(
        subject="[PFMES] 2차 인증 번호 안내",
        recipients=[email],
        body=f"인증 번호: [{otp}]\n\n본인 확인을 위해 위 인증 번호를 입력해 주세요. (유효 시간 5분)",
        subtype=MessageType.plain
    )
    
    fm = FastMail(conf)
    try:
        await fm.send_message(message)
        logger.info(f"OTP email sent to {email}")
    except Exception as e:
        logger.error(f"Failed to send OTP email to {email}: {e}")
        raise e

def store_otp(empid: str, otp: str):
    otp_cache[empid] = otp

def verify_otp(empid: str, otp: str) -> bool:
    stored_otp = otp_cache.get(empid)
    if stored_otp and stored_otp == otp:
        del otp_cache[empid]
        return True
    return False
