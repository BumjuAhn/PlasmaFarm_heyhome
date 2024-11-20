import requests
import json

def load_access_token(file_path):
    """Load ACCESS_TOKEN from a JSON file."""
    try:
        with open(file_path, 'r') as file:
            token_data = json.load(file)
            ACCESS_TOKEN = token_data.get("access_token")
            if not ACCESS_TOKEN:
                print("Error: ACCESS_TOKEN not found in token.json.")
                return None
            return ACCESS_TOKEN
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return None
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in token.json.")
        return None


def load_config(file_path):
    """Load configuration from a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return None
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in config.json.")
        return None


def get_device_list(ACCESS_TOKEN, BASE_URL):
    """Fetch the list of devices from HeyHome API."""
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
    # 파일 경로
    CONFIG_FILE_PATH = "config.json"
    TOKEN_FILE_PATH = "token.json"

    # Load configuration
    config = load_config(CONFIG_FILE_PATH)
    if not config:
        print("Failed to load configuration. Exiting.")
        exit()

    BASE_URL = config.get("base_url")
    if not BASE_URL:
        print("Error: BASE_URL not found in config.json.")
        exit()

    # Load ACCESS_TOKEN
    ACCESS_TOKEN = load_access_token(TOKEN_FILE_PATH)

    # Fetch device list
    if ACCESS_TOKEN:
        get_device_list(ACCESS_TOKEN, BASE_URL)
