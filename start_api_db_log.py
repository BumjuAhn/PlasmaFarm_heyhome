import logging
import requests
import json
import csv
import time
import mysql.connector
from datetime import datetime

# 로그 설정
LOG_FILE = "log_file.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# JSON 파일 읽기 함수
def read_json(filename):
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except Exception as e:
        logging.error(f"Error reading {filename}: {e}")
        return {}

# CSV 저장 함수 (필요할 경우)
def save_steps_to_csv(filename):
    steps = [
        {"description": "Turning ON fog", "power1": True, "power2": False, "power3": True, "duration": 60 * 20},
        {"description": "Turning OFF fog", "power1": False, "power2": False, "power3": True, "duration": 60 * 40},
        {"description": "Turning ON plasma", "power1": False, "power2": True, "power3": True, "duration": 60 * 20},
        {"description": "Turning OFF plasma", "power1": False, "power2": False, "power3": True, "duration": 60 * 40},
        {"description": "Turning ON fog and plasma", "power1": True, "power2": True, "power3": True, "duration": 60 * 20},
        {"description": "Turning OFF fog and plasma", "power1": False, "power2": False, "power3": True, "duration": 60 * 40},
    ]

    try:
        with open(filename, "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["description", "power1", "power2", "power3", "duration"])
            writer.writeheader()
            writer.writerows(steps)
        logging.info(f"Steps saved to {filename}")
    except Exception as e:
        logging.error(f"Error saving steps to {filename}: {e}")

# CSV 읽기 함수
def load_steps_from_csv(filename):
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
        logging.info(f"Steps loaded from {filename}")
    except Exception as e:
        logging.error(f"Error reading {filename}: {e}")
    return steps

# DB 초기화 함수
def initialize_db(db_config):
    try:
        conn = mysql.connector.connect(**db_config)
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
        logging.info("Database initialized successfully.")
    except mysql.connector.Error as e:
        logging.error(f"Error initializing database: {e}")

# DB 저장 함수
def save_to_db(db_config, device_id, states, description):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO power_status (timestamp, device_id, fog, plasma, pump, description)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            timestamp,
            device_id,
            states.get("power1", False),
            states.get("power2", False),
            states.get("power3", False),
            description,
        ))
        conn.commit()
        conn.close()
        logging.info(f"State saved to database: {states}, Description: {description}")
    except mysql.connector.Error as e:
        logging.error(f"Error saving to database: {e}")

# 멀티탭 제어 함수
def control_power_strip_ports(base_url, headers, device_id, states, description):
    url = f"{base_url}/control/{device_id}"
    payload = {"requirments": states}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            logging.info(f"Device {device_id} updated successfully: {states}, Description: {description}")
            return True
        else:
            logging.warning(f"Failed to update device {device_id}. Status: {response.status_code}, Response: {response.text}")
            return False
    except requests.RequestException as e:
        logging.error(f"Error during API request: {e}")
        return False

# 주기적 제어 함수
def cycle_control(base_url, headers, db_config, device_id, steps):
    start_time = time.time()
    last_time = start_time
    total_runtime = 10 * 60 * 60
    current_step = 0

    while True:
        current_time = time.time()
        elapsed_time = current_time - last_time
        total_elapsed_time = current_time - start_time

        if total_elapsed_time >= total_runtime:
            logging.info("Total runtime of 10 hours reached. Stopping the program.")
            break

        if elapsed_time >= steps[current_step]["duration"]:
            try:
                step = steps[current_step]
                logging.info(f"Executing step: {step['description']}")
                success = control_power_strip_ports(base_url, headers, device_id, step["states"], step["description"])
                if success:
                    save_to_db(db_config, device_id, step["states"], step["description"])
            except Exception as e:
                logging.error(f"Error during step: {steps[current_step]['description']}. Error: {e}")
            finally:
                last_time = current_time
                current_step = (current_step + 1) % len(steps)

# 메인 실행
if __name__ == "__main__":
    CONFIG_FILE = "config.json"
    TOKEN_FILE = "token.json"
    DB_CONFIG_FILE = "db_config.json"
    STEPS_FILE = "steps.csv"

    config = read_json(CONFIG_FILE)
    token_data = read_json(TOKEN_FILE)
    db_config = read_json(DB_CONFIG_FILE)

    BASE_URL = config.get("base_url", "")
    ACCESS_TOKEN = token_data.get("access_token", "")

    HEADERS = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    DEVICE_ID = "50450710e8db84f198f8"

    initialize_db(db_config)

    steps = load_steps_from_csv(STEPS_FILE)
    if not steps:
        logging.error("No steps loaded. Exiting program.")
        exit()

    try:
        logging.info("Starting cycle control...")
        cycle_control(BASE_URL, HEADERS, db_config, DEVICE_ID, steps)
    except KeyboardInterrupt:
        logging.info("Cycle control stopped manually.")
