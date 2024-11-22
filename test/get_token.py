from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv, set_key

# .env 파일 로드
load_dotenv()

# AES256 암호화 클래스
class AES256:
    def __init__(self, appKey):
        self.appKey = appKey

    def encrypt(self, text):
        key = self.appKey[:32].encode('utf-8')
        iv = self.appKey[:16].encode('utf-8')
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted = cipher.encrypt(pad(text.encode('utf-8'), AES.block_size))
        return base64.urlsafe_b64encode(encrypted).decode('utf-8')

    def decrypt(self, cipherText):
        key = self.appKey[:32].encode('utf-8')
        iv = self.appKey[:16].encode('utf-8')
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decodedBytes = base64.urlsafe_b64decode(cipherText)
        decrypted = unpad(cipher.decrypt(decodedBytes), AES.block_size)
        return decrypted.decode('utf-8')

def is_token_expired():
    """Check if the token is expired using .env values."""
    expires_in = os.getenv("EXPIRES_IN")
    issued_at = os.getenv("ISSUED_AT")

    if not expires_in or not issued_at:
        return True  # 만료 정보가 없으면 토큰을 새로 발급받도록 함

    issued_at_datetime = datetime.strptime(issued_at, "%Y-%m-%dT%H:%M:%S")
    expires_at = issued_at_datetime + timedelta(seconds=int(expires_in))
    return datetime.now() >= expires_at

def get_auth_token():
    """Authenticate with the API and get a new token."""
    app_key = os.getenv("APP_KEY")
    if not app_key:
        print("Error: APP_KEY is not set in .env file.")
        return None

    aes256 = AES256(app_key)

    json_data = {
        "client_id": os.getenv("CLIENT_ID"),
        "client_secret": os.getenv("CLIENT_SECRET"),
        "grant_type": "password",
        "username": os.getenv("USERNAME"),
        "password": os.getenv("PASSWORD")
    }

    # 필수 필드 확인
    for key, value in json_data.items():
        if not value:
            print(f"Error: {key} is not set in .env file.")
            return None

    encrypted_data = aes256.encrypt(json.dumps(json_data))
    token_url = f"{os.getenv('BASE_URL')}/token"

    response = requests.post(
        token_url,
        json={"data": encrypted_data}
    )

    if response.status_code == 200:
        token_data = response.json()
        # issued_at 추가
        token_data["issued_at"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        return token_data
    else:
        print("Error fetching token:", response.status_code, response.text)
        return None

def save_token_to_env(token_data):
    """Save token data to .env."""
    env_file = '.env'
    set_key(env_file, "ACCESS_TOKEN", token_data.get("access_token", ""))
    set_key(env_file, "TOKEN_TYPE", token_data.get("token_type", ""))
    set_key(env_file, "REFRESH_TOKEN", token_data.get("refresh_token", ""))
    set_key(env_file, "EXPIRES_IN", str(token_data.get("expires_in", "")))
    set_key(env_file, "SCOPE", token_data.get("scope", ""))
    set_key(env_file, "ISSUED_AT", token_data.get("issued_at", ""))
    print("Token data updated in .env")

def get_valid_token():
    """Ensure a valid token is available and return it."""
    access_token = os.getenv("ACCESS_TOKEN")

    if access_token and not is_token_expired():
        print("Token is valid.")
        return {
            "access_token": access_token,
            "token_type": os.getenv("TOKEN_TYPE"),
            "refresh_token": os.getenv("REFRESH_TOKEN"),
            "expires_in": os.getenv("EXPIRES_IN"),
            "scope": os.getenv("SCOPE"),
            "issued_at": os.getenv("ISSUED_AT"),
        }

    print("Token is expired or not available. Fetching a new one...")
    new_token_data = get_auth_token()
    if new_token_data:
        save_token_to_env(new_token_data)
        return new_token_data
    return None

if __name__ == "__main__":
    try:
        # 유효한 토큰 확보
        token_data = get_valid_token()

        if token_data:
            print("Token is valid or has been refreshed.")
            # 필요한 작업 수행
        else:
            print("Failed to acquire a valid token. Exiting program.")

    except KeyboardInterrupt:
        print("\nKeyboard interrupt received. Exiting program.")
    except Exception as e:
        print(f"An error occurred: {e}")
