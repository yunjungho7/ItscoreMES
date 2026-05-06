import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .config import settings
from .logging import logger

def send_otp_email(to_email: str, otp_code: str):
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning("SMTP settings not configured. Email OTP not sent.")
        logger.info(f"OTP for {to_email}: {otp_code}")
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL or settings.SMTP_USER}>"
        msg['To'] = to_email
        msg['Subject'] = f"[NEWMES] 인증 번호: {otp_code}"

        body = f"""
        <html>
        <body>
            <h3>NEWMES 시스템 로그인 인증</h3>
            <p>로그인을 위해 아래의 인증 번호를 입력해 주세요.</p>
            <h2 style="color: #3b82f6;">{otp_code}</h2>
            <p>이 번호는 {settings.OTP_EXPIRE_MINUTES}분 동안 유효합니다.</p>
            <br/>
            <p>본인이 요청하지 않은 경우 이 메일을 무시하셔도 됩니다.</p>
        </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))

        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        
        return True
    except Exception as e:
        logger.error(f"Failed to send OTP email to {to_email}: {e}")
        return False
