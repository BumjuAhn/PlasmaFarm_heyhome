import requests
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

# 환경 변수 로드
BASE_URL = os.getenv("BASE_URL")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

def get_device_list():
    """Fetch the list of devices from HeyHome API."""
    if not BASE_URL:
        print("Error: BASE_URL not set in .env.")
        return None

    if not ACCESS_TOKEN:
        print("Error: ACCESS_TOKEN not set in .env.")
        return None

    device_url = f"{BASE_URL}/devices"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    # API 호출
    response = requests.get(device_url, headers=headers)

    if response.status_code == 200:
        devices = response.json()
        print("Device List:")
        for device in devices:
            print(f"- ID: {device['id']}, Name: {device['name']}, Type: {device['deviceType']}")
        return devices
    else:
        print("Error fetching devices:", response.status_code, response.text)
        return None


if __name__ == "__main__":
    # Fetch device list
    get_device_list()
