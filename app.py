from flask import Flask, render_template, request, redirect, url_for, jsonify
import subprocess
import os
import signal
import csv

app = Flask(__name__)

STEPS_FILE = "steps.csv"
heyhome_process = None  # 전역 변수로 프로세스 상태 관리


# CSV 파일에서 데이터 로드
def load_steps():
    steps = []
    if os.path.exists(STEPS_FILE):
        with open(STEPS_FILE, mode="r") as file:
            reader = csv.DictReader(file)
            steps = [row for row in reader]
    return steps


# CSV 파일에 데이터 저장
def save_steps(steps):
    with open(STEPS_FILE, mode="w", newline="") as file:
        fieldnames = ["description", "power1", "power2", "power3", "duration"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(steps)


@app.route('/')
def index():
    steps = load_steps()
    status = "Running" if heyhome_process else "Stopped"
    return render_template('index.html', status=status, steps=steps)


@app.route('/start', methods=['POST'])
def start_heyhome():
    global heyhome_process
    if heyhome_process:
        return jsonify({"message": "HeyHome is already running."}), 400

    # heyhome.py 실행
    try:
        heyhome_process = subprocess.Popen(
            ["python3", "heyhome.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return jsonify({"message": "HeyHome started successfully."}), 200
    except Exception as e:
        return jsonify({"message": f"Failed to start HeyHome: {str(e)}"}), 500


@app.route('/stop', methods=['POST'])
def stop_heyhome():
    global heyhome_process
    if not heyhome_process:
        return jsonify({"message": "HeyHome is not running."}), 400

    # heyhome.py 프로세스 종료
    try:
        os.kill(heyhome_process.pid, signal.SIGTERM)
        heyhome_process = None
        return jsonify({"message": "HeyHome stopped successfully."}), 200
    except Exception as e:
        return jsonify({"message": f"Failed to stop HeyHome: {str(e)}"}), 500


@app.route('/edit', methods=['GET', 'POST'])
def edit_steps():
    steps = load_steps()
    if request.method == 'POST':
        # 업데이트된 데이터를 CSV에 저장
        updated_steps = []
        for i in range(len(steps)):
            updated_steps.append({
                "description": request.form[f"description_{i}"],
                "power1": request.form[f"power1_{i}"],
                "power2": request.form[f"power2_{i}"],
                "power3": request.form[f"power3_{i}"],
                "duration": request.form[f"duration_{i}"]
            })
        save_steps(updated_steps)
        return redirect(url_for('index'))
    return render_template('edit.html', steps=steps)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
