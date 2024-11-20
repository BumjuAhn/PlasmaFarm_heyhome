import requests
import json

# 헤이홈 API 정보
BASE_URL = "https://goqual.io/openapi"
DEVICE_ID = "ebde650d0bafd44afcyggh"  # 제어할 스마트 멀티탭의 디바이스 ID
ACCESS_TOKEN = "81d9ebf7-dd6c-4918-bd5d-b0a26fd49cb7"  # 헤이홈 API 액세스 토큰

# 헤더 정보 (인증)
HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

def control_power_strip(device_id, state):
    """
    멀티탭의 전원을 제어하는 함수
    :param device_id: 제어할 장치의 ID
    :param state: True (켜기) 또는 False (끄기)
    """
    url = f"{BASE_URL}/control/{device_id}"
    payload = {
        "requirments": {
            "power": state
        }
    }
    try:
        response = requests.post(url, headers=HEADERS, data=json.dumps(payload))
        if response.status_code == 200:
            print(f"Device {device_id} turned {'on' if state else 'off'} successfully.")
        else:
            print(f"Failed to control device. Status code: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")

# 사용 예시
if __name__ == "__main__":
    # 플러그 켜기
    # control_power_strip(DEVICE_ID, True)
    # 플러그 끄기
    control_power_strip(DEVICE_ID, False)