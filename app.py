from flask import Flask, render_template, jsonify
from threading import Thread, Event
import time
import logging
import os
from dotenv import load_dotenv
from your_existing_module import initialize_db, load_steps_from_csv, cycle_control

# .env 파일 로드
load_dotenv()

# Flask 애플리케이션 초기화
app = Flask(__name__)

# 로그 설정
LOG_FILE = "flask_cycle_control.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# 스레드 및 제어 이벤트
cycle_thread = None
stop_event = Event()

# 설정 파일 경로 및 런타임
STEPS_FILE = "steps.csv"
TOTAL_RUNTIME = 36000  # 10시간

def cycle_control_wrapper():
    """
    Wrapper function for cycle_control to handle stop_event.
    """
    steps = load_steps_from_csv(STEPS_FILE)
    if not steps:
        logging.error("No steps found in the CSV file. Exiting cycle.")
        print("[ERROR] No steps found in the CSV file. Exiting cycle.")
        return

    start_time = time.time()
    cycle_id = 1
    while time.time() - start_time < TOTAL_RUNTIME:
        for step in steps:
            if stop_event.is_set():
                logging.info("Cycle control stopped by user.")
                print("[INFO] Cycle control stopped by user.")
                return
            try:
                logging.info(f"Executing: {step['description']} (Cycle {cycle_id})")
                print(f"[INFO] Executing: {step['description']} (Cycle {cycle_id})")
                time.sleep(step["duration"])  # Simulate action duration
            except Exception as e:
                logging.error(f"Error during step: {step['description']}. Error: {e}")
                print(f"[ERROR] Error during step: {step['description']}. Error: {e}")
        cycle_id += 1

@app.route('/')
def home():
    """
    Home route to display start and stop buttons.
    """
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_cycle():
    """
    Start the cycle.
    """
    global cycle_thread, stop_event

    if cycle_thread and cycle_thread.is_alive():
        logging.info("Cycle is already running.")
        return jsonify({"status": "error", "message": "Cycle is already running."})

    stop_event.clear()
    cycle_thread = Thread(target=cycle_control_wrapper)
    cycle_thread.start()
    logging.info("Cycle started.")
    print("[INFO] Cycle started.")
    return jsonify({"status": "success", "message": "Cycle started."})

@app.route('/stop', methods=['POST'])
def stop_cycle():
    """
    Stop the cycle.
    """
    global stop_event

    if not cycle_thread or not cycle_thread.is_alive():
        logging.info("No cycle is currently running.")
        return jsonify({"status": "error", "message": "No cycle is currently running."})

    stop_event.set()
    cycle_thread.join()  # Wait for the thread to stop
    logging.info("Cycle stopped.")
    print("[INFO] Cycle stopped.")
    return jsonify({"status": "success", "message": "Cycle stopped."})

if __name__ == "__main__":
    # Initialize database
    initialize_db()

    # Start Flask server
    app.run(debug=True, host='0.0.0.0', port=5000)
