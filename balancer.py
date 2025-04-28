from flask import Flask, request, Response
import requests
import threading
import time
import os
import csv
import subprocess

app = Flask(__name__)

containers = []

# To Toggle Between RR and State-based LB
USE_RR = True  # True = Round Robin, False = Least-Requests

rr_count = 0  # Round Robin counter
lock = threading.Lock()

# to track active request count per container (for state-based LB)
request_count = {}

# Saving log for analysis
REQUEST_LOG_FILE = "./logs/detailed_log.csv"
if not os.path.exists(REQUEST_LOG_FILE):
    os.makedirs(os.path.dirname(REQUEST_LOG_FILE), exist_ok=True)
    with open(REQUEST_LOG_FILE, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "container_url", "response_time", "status_code"])

# for debugging to see if the request is received
DEBUG_FILE = "./logs/request_log.txt"
if not os.path.exists(DEBUG_FILE):
    os.makedirs(os.path.dirname(DEBUG_FILE), exist_ok=True)

def update_container_list():
    global containers, request_count
    try:
        output = subprocess.check_output(["podman", "ps", "--format", "{{.Names}} {{.Ports}}"]).decode("utf-8")
        new_containers = []
        new_request_count = {}
        for line in output.strip().split("\n"):
            if line.startswith("assign1-"):
                parts = line.split()
                if len(parts) == 2:
                    port_info = parts[1]
                    port = port_info.split(":")[1].split("->")[0]
                    url = f"http://localhost:{port}/watermark"
                    new_containers.append(url)
                    new_request_count[url] = 0
        if new_containers:
            containers = new_containers
            request_count = new_request_count
    except Exception as e:
        print(f"Failed to update container list: {e}")

# main route (post request)
@app.route("/watermark", methods=["POST"])
def route_request():
    global rr_count

    update_container_list()

    try:
        with open(DEBUG_FILE, "a") as f:
            f.write(f"{time.time()}\n")
    except Exception as e:
        print(f"Error: {e}")

    with lock:
        if not containers:
            return {"error": "No Container Built"}, 503

        if USE_RR:
            target = containers[rr_count % len(containers)]
            rr_count += 1
        else:
            target = min(request_count, key=request_count.get)
            request_count[target] += 1

    try:
        files = {'image': request.files['image']}
        data = {'watermark-size': request.form['watermark-size']}

        start_time = time.time()
        res = requests.post(target, files=files, data=data)
        response_time = time.time() - start_time

        with open(REQUEST_LOG_FILE, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([start_time, target, response_time, res.status_code])

        print(f"[{res.status_code}] Forwarded to {target} in {response_time:.4f} sec")
        return Response(res.content, status=res.status_code, content_type=res.headers.get('Content-Type', 'image/jpeg'))

    except Exception as e:
        print(f"Error forwarding request: {e}")
        return {"error": str(e)}, 500

    finally:
        if not USE_RR:
            with lock:
                if target in request_count:
                    request_count[target] = max(0, request_count[target] - 1)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, threaded=True)
