import requests
import json
import os

def load_token(file_path):
    """Load ACCESS_TOKEN from token.json."""
    if not os.path.exists(file_path):
        print("Error: token.json not found. Please obtain a valid token first.")
        return None
    with open(file_path, 'r') as file:
        try:
            token_data = json.load(file)
            ACCESS_TOKEN = token_data.get("access_token")
            if not ACCESS_TOKEN:
                print("Error: ACCESS_TOKEN not found in token.json.")
                return None
            return ACCESS_TOKEN
        except json.JSONDecodeError:
            print("Error: Invalid JSON format in token.json.")
            return None


def load_config(file_path):
    """Load configuration from config.json."""
    if not os.path.exists(file_path):
        print("Error: config.json not found.")
        return None
    with open(file_path, 'r') as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            print("Error: Invalid JSON format in config.json.")
            return None


def get_device_status(ACCESS_TOKEN, BASE_URL, device_id):
    """Fetch the current status of a device."""
    status_url = f"{BASE_URL}/device/{device_id}"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

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
        # Paths to config.json and token.json
        CONFIG_FILE_PATH = "config.json"
        TOKEN_FILE_PATH = "token.json"

        # Load configuration
        config = load_config(CONFIG_FILE_PATH)
        if not config:
            print("Exiting program due to missing or invalid configuration.")
            exit(1)

        BASE_URL = config.get("base_url")
        if not BASE_URL:
            print("Error: BASE_URL not found in config.json.")
            exit(1)

        # Load ACCESS_TOKEN
        ACCESS_TOKEN = load_token(TOKEN_FILE_PATH)
        if not ACCESS_TOKEN:
            print("Exiting program due to missing or invalid token.")
            exit(1)

        # Device ID to check status
        DEVICE_ID = "50450710e8db84f198f8"
        get_device_status(ACCESS_TOKEN, BASE_URL, DEVICE_ID)

    except KeyboardInterrupt:
        print("\nKeyboard interrupt received. Exiting program.")
    except Exception as e:
        print(f"An error occurred: {e}")
