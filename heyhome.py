import time
import logging
import requests
from config import BASE_URL, DEVICE_ID
from auth import get_valid_token
from database import initialize_db, save_to_db
from utility import load_steps_from_csv, create_cycles_from_steps

def cycle_control(steps, total_runtime=36000):
    """Control the power strip based on cycles for a given runtime."""
    token = get_valid_token()
    if not token:
        logging.error("Failed to obtain a valid token.")
        return

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    cycles = create_cycles_from_steps(steps)

    start_time = time.time()
    cycle_id = 1

    while time.time() - start_time < total_runtime:
        for cycle in cycles:
            for step in cycle:
                try:
                    logging.info(f"Executing: {step['description']} (Cycle {cycle_id})")
                    response = requests.post(
                        f"{BASE_URL}/control/{DEVICE_ID}",
                        headers=headers,
                        json={"requirments": step["states"]}
                    )
                    if response.status_code == 200:
                        logging.info(f"Device updated: {step['states']}")
                        save_to_db(DEVICE_ID, step["states"], step["description"], cycle_id)
                    else:
                        logging.error(f"Failed to update device: {response.status_code}, {response.text}")
                except Exception as e:
                    logging.error(f"Error during step execution: {e}")
                time.sleep(step["duration"])
            cycle_id += 1
            if time.time() - start_time >= total_runtime:
                break

def main():
    """Main execution entry point."""
    STEPS_FILE = "steps.csv"

    initialize_db()
    steps = load_steps_from_csv(STEPS_FILE)

    if not steps:
        logging.error("No steps found. Exiting.")
        return

    logging.info("Starting cycle control.")
    cycle_control(steps)

if __name__ == "__main__":
    main()
