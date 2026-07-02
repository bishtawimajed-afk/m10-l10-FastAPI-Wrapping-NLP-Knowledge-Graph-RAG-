import os
from datetime import datetime, timedelta, timezone
from fastapi import Header, HTTPException, status, Depends, Security
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from jose import jwt, JWTError

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

def get_jwt_secret() -> str:
    return os.environ.get("JWT_SECRET", "fallback-secret-string-for-local-testing-purposes-only")

def get_jwt_algorithm() -> str:
    return os.environ.get("JWT_ALGORITHM", "HS256")

def create_access_token(subject: str, expires_minutes: int = 60) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, get_jwt_secret(), algorithm=get_jwt_algorithm())

def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    valid_key = os.environ.get("API_KEY_VALID", os.environ.get("API_KEY", "my-super-secure-dev-api-key"))
    if not api_key or api_key != valid_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or Invalid API Key"
        )
    return api_key

def verify_jwt(token: str = Depends(oauth2_scheme)) -> dict:
    if not token or token == "None":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or Expired Token"
        )
    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=[get_jwt_algorithm()])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or Expired Token"
        )

def verify_api_key_or_jwt(
    api_key: str = Security(api_key_header),
    token: str = Depends(oauth2_scheme)
):
    valid_key = os.environ.get("API_KEY_VALID", os.environ.get("API_KEY", "my-super-secure-dev-api-key"))
    
    if api_key and api_key == valid_key:
        return

    if token and token != "None":
        try:
            jwt.decode(token, get_jwt_secret(), algorithms=[get_jwt_algorithm()])
            return
        except JWTError:
            pass

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated. Valid API Key or JWT Bearer token required."
    )