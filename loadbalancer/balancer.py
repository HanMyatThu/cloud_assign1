from flask import Flask, request, Response
import requests
import threading

app = Flask(__name__)

containers = [
  "http://localhost:8081/watermark",
  "http://localhost:8082/watermark"
]

rr_count = 0 
# to avoid simultaneous access
lock = threading.Lock() 

@app.route("/watermark", methods=["POST"])
def route_request():
  global rr_count

  if not containers:
    return {"error": "No available container instances"}, 503

  # Round Robin
  with lock:
    target = containers[rr_count % len(containers)]
    rr_count += 1

  try:
    files = {'image': request.files['image']}
    data = {'watermark-size': request.form['watermark-size']}
    res = requests.post(target, files=files, data=data)
    print(f"Forwarding request to: {target}")
    return Response(res.content, status=res.status_code, content_type=res.headers.get('Content-Type', 'application/octet-stream'))

  except Exception as e:
    return {"error": str(e)}, 500

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=8080)
