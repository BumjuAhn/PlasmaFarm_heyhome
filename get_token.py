from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import requests
import json
import os
from datetime import datetime, timedelta

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


def load_config(file_path):
    """Load configuration from a JSON file."""
    with open(file_path, 'r') as file:
        return json.load(file)


def load_token(file_path):
    """Load token data from token.json."""
    if not os.path.exists(file_path):
        return None
    with open(file_path, 'r') as file:
        try:
            token_data = json.load(file)
            return token_data
        except json.JSONDecodeError:
            print("Error: Invalid JSON format in token.json.")
            return None


def save_token(file_path, token_data):
    """Save token data to token.json."""
    with open(file_path, 'w') as file:
        json.dump(token_data, file, indent=4)
    print("Token saved to", file_path)


def is_token_expired(token_data):
    """Check if the token is expired."""
    expires_in = token_data.get("expires_in")
    if not expires_in:
        return True  # 만료 정보가 없으면 새로 발급

    issued_at = token_data.get("issued_at")
    if not issued_at:
        return True

    # 현재 시각과 만료 시각 비교
    issued_at_datetime = datetime.strptime(issued_at, "%Y-%m-%dT%H:%M:%S")
    expires_at = issued_at_datetime + timedelta(seconds=expires_in)
    return datetime.now() >= expires_at


def get_auth_token(config):
    """Authenticate with HeyHome API and get the token."""
    aes256 = AES256(config['app_key'])

    json_data = {
        "client_id": config['client_id'],
        "client_secret": config['client_secret'],
        "grant_type": "password",
        "username": config['username'],
        "password": config['password']
    }

    encrypted_data = aes256.encrypt(json.dumps(json_data))
    token_url = f"{config['base_url']}/token"
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


def get_valid_token(config, token_file_path):
    """Ensure a valid token is available and return it."""
    token_data = load_token(token_file_path)

    if token_data and not is_token_expired(token_data):
        print("Token is valid.")
        return token_data

    print("Token is expired or not available. Fetching a new one...")
    new_token_data = get_auth_token(config)
    if new_token_data:
        save_token(token_file_path, new_token_data)
    return new_token_data


if __name__ == "__main__":
    try:
        # Load configuration
        config_file_path = "config.json"
        token_file_path = "token.json"

        config = load_config(config_file_path)

        # Ensure valid token
        token_data = get_valid_token(config, token_file_path)

        if token_data:
            print("Token is valid or has been refreshed. Program will now exit.")
        else:
            print("Failed to acquire a valid token. Exiting program.")
        
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received. Exiting program.")
    except Exception as e:
        print(f"An error occurred: {e}")
