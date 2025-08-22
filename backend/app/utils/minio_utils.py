import os
import io
import time
import threading
import urllib.parse
import requests
import urllib3
from minio import Minio
from dotenv import load_dotenv

load_dotenv()

AUTH_URL = os.getenv("AUTH_URL")
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"
MINIO_REGION = os.getenv("MINIO_REGION")
MINIO_USERNAME = os.getenv("MINIO_USERNAME")
MINIO_PASSWORD = os.getenv("MINIO_PASSWORD")
MINIO_BUCKET = os.getenv("MINIO_BUCKET")

# cache for token
_token_cache = {"token": None, "expires_at": 0}
_lock = threading.Lock()


def _refresh_token():
    """Fetches a fresh Keycloak token and updates the cache."""
    payload = {"username": MINIO_USERNAME, "password": MINIO_PASSWORD}
    encoded_payload = urllib.parse.urlencode(payload)
    headers = {"accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(AUTH_URL, data=encoded_payload, headers=headers)
    response.raise_for_status()
    token_json = response.json()
    if "access_token" not in token_json:
        raise Exception("access_token not found in auth response")

    token = token_json["access_token"]
    expires_in = token_json.get("expires_in", 300)  # default 5 minutes
    _token_cache["token"] = token
    _token_cache["expires_at"] = time.time() + expires_in - 60  # refresh 1min before expiry


def get_auth_token():
    """Return cached token, trigger refresh if near expiry."""
    now = time.time()
    with _lock:
        if not _token_cache["token"] or now >= _token_cache["expires_at"]:
            _refresh_token()
        return _token_cache["token"]


def _schedule_background_refresh():
    """Runs in a thread and refreshes token periodically."""
    while True:
        time.sleep(60)  # check every minute
        now = time.time()
        with _lock:
            if not _token_cache["token"] or now >= _token_cache["expires_at"]:
                try:
                    _refresh_token()
                    print("[MinIO] Token refreshed in background")
                except Exception as e:
                    print(f"[MinIO] Failed to refresh token: {e}")


# Start refresher thread
threading.Thread(target=_schedule_background_refresh, daemon=True).start()


class TokenPoolManager(urllib3.PoolManager):
    """Injects Bearer token into every MinIO HTTP request."""
    def request(self, method, url, **kwargs):
        token = get_auth_token()
        headers = kwargs.get("headers", {})
        headers["Authorization"] = f"Bearer {token}"
        kwargs["headers"] = headers
        return super().request(method, url, **kwargs)


def get_minio_client() -> Minio:
    http_client = TokenPoolManager()
    return Minio(
        endpoint=MINIO_ENDPOINT,
        access_key="",
        secret_key="",
        secure=MINIO_SECURE,
        region=MINIO_REGION,
        http_client=http_client,
    )


async def upload_file(file_data: bytes, config_id: int) -> str:
    client = get_minio_client()
    filename = f"config_{config_id}.json"
    object_name = os.path.join(str(config_id), filename)

    client.put_object(
        MINIO_BUCKET,
        object_name,
        io.BytesIO(file_data),
        len(file_data),
    )
    return object_name


def list_files(config_id: int):
    client = get_minio_client()
    return [obj.object_name for obj in client.list_objects(MINIO_BUCKET, prefix=f"{config_id}/", recursive=True)]


def download_file(config_id: int, log_name: str):
    client = get_minio_client()
    log_path = f"{config_id}/{log_name}"
    return client.presigned_get_object(MINIO_BUCKET, log_path)


def delete_file(config_id: int, log_name: str):
    client = get_minio_client()
    log_path = f"{config_id}/{log_name}"
    client.remove_object(MINIO_BUCKET, log_path)
