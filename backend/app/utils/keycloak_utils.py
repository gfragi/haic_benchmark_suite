import requests
from jose import jwt, JWTError
from fastapi import HTTPException, status
import os
from dotenv import load_dotenv


load_dotenv() 

# Replace these values with your actual Keycloak settings
KEYCLOAK_SERVER_URL = os.getenv("KEYCLOAK_SERVER_URL", "http://localhost:8080/auth")
KEYCLOAK_REALM_NAME = os.getenv("KEYCLOAK_REALM_NAME", "myrealm")
KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET", "mysecret")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "myclient")

ISSUER = f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM_NAME}"
JWKS_URL = f"{ISSUER}/protocol/openid-connect/certs"

# Optionally cache the JWKS to avoid fetching on every request
_jwks_cache = None

def get_jwks():
    global _jwks_cache
    if _jwks_cache is None:
        resp = requests.get(JWKS_URL)
        if resp.status_code == 200:
            _jwks_cache = resp.json()
        else:
            raise Exception("Failed to retrieve JWKS from Keycloak.")
    return _jwks_cache

def decode_jwt_token(token: str):
    """Decode and validate the JWT token from Keycloak."""
    try:
        # 1. Get the 'kid' (key ID) from the token header
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        if not kid:
            raise HTTPException(status_code=401, detail="Invalid token header.")

        # 2. Retrieve the JWKS and find the correct public key
        jwks = get_jwks()
        public_key = None
        for key in jwks["keys"]:
            if key["kid"] == kid:
                public_key = key
                break

        if not public_key:
            raise HTTPException(status_code=401, detail="Public key not found.")

        # 3. Decode the token using the public key
        #    Keycloak generally uses RS256
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=KEYCLOAK_CLIENT_ID,
            issuer=ISSUER
        )

        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token validation error",
        ) from e