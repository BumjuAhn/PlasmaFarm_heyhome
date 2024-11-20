import requests
import json

# json 파일에서 설정 읽기
def read_json(filename):
    with open(filename, "r") as file:
        return json.load(file)

# 파일 경로
CONFIG_FILE = "config.json"
TOKEN_FILE = "token.json"

# 설정 읽기
config = read_json(CONFIG_FILE)
token_data = read_json(TOKEN_FILE)

BASE_URL = config["base_url"]  # config.json에서 base_url 불러오기
ACCESS_TOKEN = token_data["access_token"]  # token.json에서 access_token 불러오기

# 헤더 정보
HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

def control_power_strip_ports(device_id, states):
    """
    멀티탭의 여러 포트를 제어하는 함수
    :param device_id: 제어할 장치의 ID
    :param states: 포트 상태를 나타내는 딕셔너리 (예: {"power1": True, "power2": False})
    """
    url = f"{BASE_URL}/control/{device_id}"
    payload = {
        "requirments": states  # 포트 상태를 전달
    }
    try:
        response = requests.post(url, headers=HEADERS, data=json.dumps(payload))
        if response.status_code == 200:
            print(f"Device {device_id} ports updated successfully.")
        else:
            print(f"Failed to update device ports. Status code: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")

# 사용 예시
if __name__ == "__main__":
    # 포트 상태 설정 (True: 켜기, False: 끄기)
    port_states = {
        "power1": False,
        # "power2": False,
        # "power3": True,
        # "power4": False,
        # "power5": False
    }
    # 스마트 멀티탭 디바이스 ID
    DEVICE_ID = "50450710e8db84f198f8"
    
    # 멀티탭 제어 실행
    control_power_strip_ports(DEVICE_ID, port_states)
