import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Union, Any
from core.config import settings
import ipaddress
from fastapi import Request
from loguru import logger

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

def is_internal_ip(request: Request) -> bool:
    # Get client IP from headers if behind a proxy
    client_ip = request.headers.get("x-real-ip") or request.headers.get("x-forwarded-for") or request.client.host
    
    # In case of multiple IPs in X-Forwarded-For, take the first one
    if client_ip and "," in client_ip:
        client_ip = client_ip.split(",")[0].strip()
        
    logger.info(f"Checking IP: {client_ip}")
    
    if not client_ip:
        return False
        
    try:
        ip_obj = ipaddress.ip_address(client_ip)
        internal_ranges = [r.strip() for r in settings.INTERNAL_IP_RANGES.split(",")]
        
        for r in internal_ranges:
            if ipaddress.ip_network(r).overlaps(ipaddress.ip_network(f"{client_ip}/32")):
                return True
        return False
    except ValueError as e:
        logger.error(f"Invalid IP address format: {client_ip} - {e}")
        return False
