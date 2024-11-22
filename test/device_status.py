import requests
import json
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

# 환경 변수 로드
BASE_URL = os.getenv("BASE_URL")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
DEVICE_ID = os.getenv("DEVICE_ID")

def get_device_status(access_token, base_url, device_id):
    """Fetch the current status of a device."""
    if not access_token or not base_url or not device_id:
        print("Error: Required environment variables are missing. Please check .env file.")
        return None

    status_url = f"{base_url}/device/{device_id}"
    headers = {"Authorization": f"Bearer {access_token}"}

    print(f"Fetching status for device {device_id}...")
    response = requests.get(status_url, headers=headers)

    if response.status_code == 200:
        status = response.json()
        print(f"Current status of device {device_id}:")
        print(json.dumps(status, indent=4))
        return status
    else:
        print(f"Failed to fetch status for device {device_id}:", response.status_code, response.text)
        return None


if __name__ == "__main__":
    try:
        # 환경 변수 체크
        if not BASE_URL:
            print("Error: BASE_URL not set in .env file.")
            exit(1)
        if not ACCESS_TOKEN:
            print("Error: ACCESS_TOKEN not set in .env file.")
            exit(1)
        if not DEVICE_ID:
            print("Error: DEVICE_ID not set in .env file.")
            exit(1)

        # 장치 상태 가져오기
        get_device_status(ACCESS_TOKEN, BASE_URL, DEVICE_ID)

    except KeyboardInterrupt:
        print("\nKeyboard interrupt received. Exiting program.")
    except Exception as e:
        print(f"An error occurred: {e}")
