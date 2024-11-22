import os
import requests
import json
import base64
from datetime import datetime, timedelta
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from dotenv import set_key
from config import BASE_URL, LOG_FILE
import logging

# AES256 암호화 클래스
class AES256:
    def __init__(self, app_key):
        self.key = app_key[:32].encode('utf-8')
        self.iv = app_key[:16].encode('utf-8')

    def encrypt(self, text):
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        encrypted = cipher.encrypt(pad(text.encode('utf-8'), AES.block_size))
        return base64.urlsafe_b64encode(encrypted).decode('utf-8')

    def decrypt(self, cipher_text):
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        decoded = base64.urlsafe_b64decode(cipher_text)
        decrypted = unpad(cipher.decrypt(decoded), AES.block_size)
        return decrypted.decode('utf-8')

# 토큰 처리
def is_token_expired(issued_at, expires_in):
    """Check if the token is expired."""
    expires_at = issued_at + timedelta(seconds=int(expires_in))
    return datetime.now() >= expires_at

def fetch_token(app_key, credentials):
    """Fetch a new token from the API."""
    aes = AES256(app_key)
    encrypted_data = aes.encrypt(json.dumps(credentials))
    try:
        response = requests.post(f"{BASE_URL}/token", json={"data": encrypted_data})
        response.raise_for_status()
        token_data = response.json()
        token_data["issued_at"] = datetime.now()
        return token_data
    except requests.RequestException as e:
        logging.error(f"Error fetching token: {e}")
        return None

def save_token_to_env(token_data):
    """Save token data to .env."""
    try:
        for key, value in token_data.items():
            set_key('.env', key.upper(), str(value))
        logging.info("Token data updated in .env")
    except Exception as e:
        logging.error(f"Error saving token to .env: {e}")

def get_valid_token():
    """Ensure a valid token is available and return it."""
    access_token = os.getenv("ACCESS_TOKEN")
    if access_token:
        issued_at_str = os.getenv("ISSUED_AT")
        expires_in = os.getenv("EXPIRES_IN")
        
        if issued_at_str and expires_in:
            # ISO 8601 형식의 ISSUED_AT 처리
            issued_at = datetime.strptime(issued_at_str, "%Y-%m-%dT%H:%M:%S")
            if not is_token_expired(issued_at, int(expires_in)):
                logging.info("Using valid token from .env")
                return access_token

    logging.info("Token expired or unavailable. Fetching new one.")
    credentials = {
        "client_id": os.getenv("CLIENT_ID"),
        "client_secret": os.getenv("CLIENT_SECRET"),
        "grant_type": "password",
        "username": os.getenv("USERNAME"),
        "password": os.getenv("PASSWORD")
    }
    app_key = os.getenv("APP_KEY")
    token_data = fetch_token(app_key, credentials)
    if token_data:
        save_token_to_env(token_data)
        return token_data["access_token"]
    return None

