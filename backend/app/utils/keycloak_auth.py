# app/utils/keycloak_auth.py
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from keycloak import KeycloakOpenID
import os

keycloak_openid = KeycloakOpenID(
    server_url=os.getenv("KEYCLOAK_SERVER_URL"),
    realm_name=os.getenv("KEYCLOAK_REALM_NAME"),
    client_id=os.getenv("KEYCLOAK_CLIENT_ID"),
    client_secret_key=os.getenv("KEYCLOAK_CLIENT_SECRET"),
)

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        userinfo = keycloak_openid.userinfo(token)
        if not userinfo or "sub" not in userinfo:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )
        return userinfo
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token validation failed"
        )
