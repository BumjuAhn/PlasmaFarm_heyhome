from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import requests
import json
import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv, set_key
import mysql.connector
import csv
import time

# .env 파일 로드
load_dotenv()

# 로그 설정
LOG_FILE = "log_file.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# 환경 변수 로드
BASE_URL = os.getenv("BASE_URL")
DEVICE_ID = os.getenv("DEVICE_ID")

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}

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

# 토큰 유효성 검증
def is_token_expired():
    """Check if the token is expired using .env values."""
    expires_in = os.getenv("EXPIRES_IN")
    issued_at = os.getenv("ISSUED_AT")

    if not expires_in or not issued_at:
        return True

    issued_at_datetime = datetime.strptime(issued_at, "%Y-%m-%dT%H:%M:%S")
    expires_at = issued_at_datetime + timedelta(seconds=int(expires_in))
    return datetime.now() >= expires_at

# 토큰 갱신
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

    for key, value in json_data.items():
        if not value:
            print(f"Error: {key} is not set in .env file.")
            return None

    encrypted_data = aes256.encrypt(json.dumps(json_data))
    token_url = f"{BASE_URL}/token"

    response = requests.post(token_url, json={"data": encrypted_data})

    if response.status_code == 200:
        token_data = response.json()
        token_data["issued_at"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        return token_data
    else:
        print("Error fetching token:", response.status_code, response.text)
        logging.error("Error fetching token:", response.status_code, response.text)
        return None

# 토큰 저장
def save_token_to_env(token_data):
    """Save token data to .env."""
    env_file = '.env'
    set_key(env_file, "ACCESS_TOKEN", token_data.get("access_token", ""))
    set_key(env_file, "TOKEN_TYPE", token_data.get("token_type", ""))
    set_key(env_file, "REFRESH_TOKEN", token_data.get("refresh_token", ""))
    set_key(env_file, "EXPIRES_IN", str(token_data.get("expires_in", "")))
    set_key(env_file, "ISSUED_AT", token_data.get("issued_at", ""))
    print("Token data updated in .env")
    logging.info("Token data updated in .env")

# 유효한 토큰 가져오기
def get_valid_token():
    """Ensure a valid token is available and return it."""
    access_token = os.getenv("ACCESS_TOKEN")

    if access_token and not is_token_expired():
        print("Token is valid.")
        logging.info("Token is valid.")
        return {
            "access_token": access_token,
            "token_type": os.getenv("TOKEN_TYPE"),
            "refresh_token": os.getenv("REFRESH_TOKEN"),
            "expires_in": os.getenv("EXPIRES_IN"),
            "scope": os.getenv("SCOPE"),
            "issued_at": os.getenv("ISSUED_AT"),
        }

    print("Token is expired or not available. Fetching a new one...")
    logging.info("Token is expired or not available. Fetching a new one...")
    new_token_data = get_auth_token()
    if new_token_data:
        save_token_to_env(new_token_data)
        return new_token_data
    return None

# 데이터베이스 초기화
def initialize_db():
    """Initialize the database."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS power_status (
                id INT AUTO_INCREMENT PRIMARY KEY,
                cycle_id INT NOT NULL,
                timestamp DATETIME NOT NULL,
                device_id VARCHAR(255) NOT NULL,
                fog BOOLEAN NOT NULL,
                plasma BOOLEAN NOT NULL,
                pump BOOLEAN NOT NULL,
                description TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()
        print("Database initialized successfully.")
        logging.info("Database initialized successfully.")
    except mysql.connector.Error as e:
        print(f"Error initializing database: {e}")
        logging.info(f"Error initializing database: {e}")

# 상태를 데이터베이스에 저장
def save_to_db(device_id, states, description, cycle_id):
    """Save the current status to the database."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO power_status (cycle_id, timestamp, device_id, fog, plasma, pump, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            cycle_id,
            timestamp,
            device_id,
            states.get("power1", False),
            states.get("power2", False),
            states.get("power3", False),
            description
        ))
        conn.commit()
        conn.close()
        print(f"State saved to database: {states}, Description: {description}, Cycle: {cycle_id}")
        logging.info(f"State saved to database: {states}, Description: {description}, Cycle: {cycle_id}")
    except mysql.connector.Error as e:
        print(f"Error saving to database: {e}")
        logging.error(f"Error saving to database: {e}")

# CSV 파일에서 단계 로드
def load_steps_from_csv(filename):
    """Load steps from CSV file."""
    steps = []
    try:
        with open(filename, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                steps.append({
                    "description": row["description"],
                    "states": {
                        "power1": row["power1"].lower() == "true",
                        "power2": row["power2"].lower() == "true",
                        "power3": row["power3"].lower() == "true",
                    },
                    "duration": int(row["duration"]),
                })
        print(f"Steps loaded from {filename}")
        logging.info(f"Steps loaded from {filename}")
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        logging.error(f"Error reading {filename}: {e}")
    return steps

# 패턴에 따라 사이클 생성
def create_cycles_from_steps(steps):
    """Create cycles based on a predefined pattern."""
    cycles = []
    cycle_patterns = [
        ["Turning ON fog", "Turning OFF fog"],  # Cycle 001
        ["Turning ON plasma", "Turning OFF plasma"],  # Cycle 002
        ["Turning ON fog and plasma", "Turning OFF fog and plasma"],  # Cycle 003
    ]
    pattern_index = 0
    while True:
        current_pattern = cycle_patterns[pattern_index]
        current_cycle = [step for step in steps if step["description"] in current_pattern]
        cycles.append(current_cycle)
        pattern_index = (pattern_index + 1) % len(cycle_patterns)
        if len(cycles) >= 1000:
            break
    return cycles

# 주기적으로 제어
def cycle_control(steps, total_runtime=36000):
    """Control the power strip based on cycles for a given runtime."""
    token_data = get_valid_token()
    if not token_data:
        print("Failed to obtain a valid token.")
        logging.info("Failed to obtain a valid token.")
        return

    headers = {
        "Authorization": f"Bearer {token_data['access_token']}",
        "Content-Type": "application/json",
    }

    cycles = create_cycles_from_steps(steps)
    start_time = time.time()
    cycle_id = 1
    while time.time() - start_time < total_runtime:
        for cycle in cycles:
            for step in cycle:
                try:
                    print(f"Executing: {step['description']} (Cycle {cycle_id})")
                    print(f"HEADERS: {headers}")
                    print(f"requirements: {step["states"]}")
                    print(f"{BASE_URL}/control/{DEVICE_ID}")
                    logging.info(f"Executing: {step['description']} (Cycle {cycle_id})")
                    response = requests.post(
                        f"{BASE_URL}/control/{DEVICE_ID}",
                        headers=headers,
                        json={"requirments": step["states"]}
                    )
                    if response.status_code == 200:
                        print(f"Device updated: {step['states']}")
                        logging.info(f"Device updated: {step['states']}")
                        save_to_db(DEVICE_ID, step["states"], step["description"], cycle_id)
                    else:
                        print(f"Failed: {response.status_code}, {response.text}")
                        logging.error(f"Failed: {response.status_code}, {response.text}")
                except Exception as e:
                    print(f"Error during step: {e}")
                    logging.error(f"Error during step: {e}")
                time.sleep(step["duration"])
            cycle_id += 1
            if time.time() - start_time >= total_runtime:
                break

# 메인 실행
if __name__ == "__main__":
    STEPS_FILE = "steps.csv"

    initialize_db()
    steps = load_steps_from_csv(STEPS_FILE)
    if steps:
        cycle_control(steps)
    else:
        print("No steps found. Exiting.")
        logging.info("No steps found. Exiting.")
