import requests
import json
import time
import mysql.connector
from datetime import datetime
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

# 환경 변수 로드
BASE_URL = os.getenv("BASE_URL")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
DEVICE_ID = os.getenv("DEVICE_ID")

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 3306)),  # 기본 포트는 3306
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}

# 헤더 설정
HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json",
}


def initialize_db():
    """
    데이터베이스 초기화 함수. 테이블이 없으면 생성.
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS power_status (
                id INT AUTO_INCREMENT PRIMARY KEY,
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
    except mysql.connector.Error as e:
        print(f"Error initializing database: {e}")


def save_to_db(device_id, states, description):
    """
    상태 데이터를 데이터베이스에 저장하는 함수.
    :param device_id: 장치 ID
    :param states: 상태 데이터 (fog, plasma, pump)
    :param description: 단계 설명
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO power_status (timestamp, device_id, fog, plasma, pump, description)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            timestamp,
            device_id,
            states.get("power1", False),  # fog
            states.get("power2", False),  # plasma
            states.get("power3", False),  # pump
            description
        ))
        conn.commit()
        conn.close()
        print(f"State saved to database: {states}, Description: {description}")
    except mysql.connector.Error as e:
        print(f"Error saving to database: {e}")


def control_power_strip_ports(device_id, states, description):
    """
    멀티탭 포트 상태를 제어하는 함수.
    :param device_id: 제어할 장치의 ID
    :param states: 포트 상태 딕셔너리
    :param description: 단계 설명
    """
    url = f"{BASE_URL}/control/{device_id}"
    payload = {"requirments": states}

    try:
        response = requests.post(url, headers=HEADERS, data=json.dumps(payload))
        if response.status_code == 200:
            print(f"Device {device_id} updated successfully: {states}, Description: {description}")
            save_to_db(device_id, states, description)  # DB 저장
        else:
            print(f"Failed to update device {device_id}. Status: {response.status_code}, Response: {response.text}")
    except requests.RequestException as e:
        print(f"Error during API request: {e}")


def cycle_control(device_id):
    """
    주기적으로 멀티탭 포트 상태를 제어하는 함수.
    에러 발생 시 프로그램이 멈추지 않도록 예외 처리를 추가.
    :param device_id: 제어할 장치의 ID
    """
    steps = [
        {"description": "Turning ON fog", "states": {"power1": True, "power2": False, "power3": True}, "delay": 60},
        {"description": "Turning OFF fog", "states": {"power1": False, "power2": False, "power3": True}, "delay": 60},
        {"description": "Turning ON plasma", "states": {"power1": False, "power2": True, "power3": True}, "delay": 60},
        {"description": "Turning OFF plasma", "states": {"power1": False, "power2": False, "power3": True}, "delay": 60},
        {"description": "Turning ON fog and plasma", "states": {"power1": True, "power2": True, "power3": True}, "delay": 60},
        {"description": "Turning OFF fog and plasma", "states": {"power1": False, "power2": False, "power3": True}, "delay": 60},
    ]

    while True:
        for step in steps:
            try:
                print(step["description"])
                control_power_strip_ports(device_id, step["states"], step["description"])
            except Exception as e:
                print(f"Error during step: {step['description']}. Error: {e}")
            finally:
                time.sleep(step["delay"])  # 각 단계별 대기 시간


if __name__ == "__main__":
    # 필수 환경 변수 체크
    if not all([BASE_URL, ACCESS_TOKEN, DEVICE_ID]):
        print("Error: Missing required environment variables. Please check your .env file.")
        exit(1)

    # 데이터베이스 초기화
    initialize_db()

    try:
        print("Starting cycle control...")
        cycle_control(DEVICE_ID)
    except KeyboardInterrupt:
        print("Cycle control stopped manually.")
