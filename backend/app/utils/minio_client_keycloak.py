import os
print("MINIO_ENDPOINT from os.environ:", os.environ.get("MINIO_ENDPOINT"))

import requests
import urllib.parse
import urllib3
from minio import Minio
from dotenv import load_dotenv
import logging

load_dotenv(dotenv_path="../../.env")  # Load environment variables from .env file

AUTH_URL = os.getenv("AUTH_URL", "https://humaine-minio-api.euprojects.net/auth/auth")
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"
MINIO_REGION = os.getenv("MINIO_REGION")
MINIO_USERNAME = os.getenv("MINIO_USERNAME")
MINIO_PASSWORD = os.getenv("MINIO_PASSWORD")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")

logging.debug("MINIO_ENDPOINT: %s", MINIO_ENDPOINT)
logging.debug("MINIO_SECURE: %s", MINIO_SECURE)
print("MINIO_ENDPOINT:", MINIO_ENDPOINT)

logging.basicConfig(level=logging.DEBUG)

def get_auth_token():
    payload = {
        "username": MINIO_USERNAME,
        "password": MINIO_PASSWORD
    }
    logging.debug("Auth payload: %s", payload)

    # URL-encode the payload for form submission
    encoded_payload = urllib.parse.urlencode(payload)
    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(AUTH_URL, data=encoded_payload, headers=headers)
    logging.debug("Request body: %s", response.request.body)

    if response.status_code != 200:
        logging.error("Auth request failed: %s - %s", response.status_code, response.text)
        raise Exception(f"Auth error: {response.status_code} - {response.text}")

    token_json = response.json()
    if "access_token" not in token_json:
        raise Exception("access_token not found in auth response")

    return token_json["access_token"]

class TokenPoolManager(urllib3.PoolManager):
    """
    A custom PoolManager that injects the Bearer token into every request.
    """
    def __init__(self, token, *args, **kwargs):
        self.token = token
        super().__init__(*args, **kwargs)

    def request(self, method, url, **kwargs):
        headers = kwargs.get("headers", {})
        headers["Authorization"] = f"Bearer {self.token}"
        kwargs["headers"] = headers
        return super().request(method, url, **kwargs)

def get_minio_client() -> Minio:
    """
    Creates a Minio client using a custom urllib3.PoolManager that injects
    the Bearer token into all HTTP requests.
    """
    token = get_auth_token()
    http_client = TokenPoolManager(token)

    return Minio(
        endpoint=MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key= MINIO_SECRET_KEY,
        secure=MINIO_SECURE,
        region=MINIO_REGION,
        http_client=http_client
    )

if __name__ == "__main__":
    try:
        token = get_auth_token()
        print("Retrieved token:", token)
        # Optionally, test the Minio client:
        minio_client = get_minio_client()
        # For example, list buckets (if allowed):
        buckets = minio_client.list_buckets()
        print("Buckets:", [bucket.name for bucket in buckets])
    except Exception as e:
        print(e)












# keycloak_openid = KeycloakOpenID(
# server_url=os.getenv("KEYCLOAK_SERVER_URL"),
# client_id=os.getenv("KEYCLOAK_CLIENT_ID"),
# realm_name=os.getenv("KEYCLOAK_REALM_NAME"),
# client_secret_key=os.getenv("KEYCLOAK_CLIENT_SECRET"),
# )

# class RequestsHTTPClient:
#     """
#     A custom HTTP client that automatically injects the Bearer token into all requests.
#     """
#     def __init__(self, token: str):
#         self.session = requests.Session()
#         self.session.headers.update({"Authorization": f"Bearer {token}"})

#     def request(self, method, url, headers=None, data=None, timeout=None):
#         # Merge any additional headers with the session’s headers
#         merged_headers = {}
#         if headers:
#             merged_headers.update(headers)
#         merged_headers.update(self.session.headers)
#         response = self.session.request(method, url, headers=merged_headers, data=data, timeout=timeout)
#         return response

# def get_keycloak_token():
#     try:
#         token = keycloak_openid.token(grant_type="client_credentials")
#         return token["access_token"]
#     except Exception as e:
#         logging.error("Error retrieving token", exc_info=True)
#         raise Exception(f"Error retrieving token: {e}")

# def get_minio_client() -> Minio:
#     """
#     Create a Minio client configured to use the bearer token from Keycloak.
#     """
#     token = get_keycloak_token()
#     http_client = RequestsHTTPClient(token)

#     # Depending on your server’s configuration you might not need access_key and secret_key.
#     return Minio(
#         endpoint=os.getenv("MINIO_ENDPOINT"),
#         access_key="",
#         secret_key="",
#         secure=(os.getenv("MINIO_SECURE", "false").lower() == "true"),
#         region=os.getenv("MINIO_REGION"),
#         http_client=http_client
#     )
