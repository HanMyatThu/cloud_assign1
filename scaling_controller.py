import time
import subprocess
import argparse
from collections import deque
import os

# configs
CONTAINER_IMAGE = "assign1"
FOLDER_PATH = "/home/vagrant/files/data:/app/data"
INITIAL_PORT = 8081
REQUEST_LOG = "./logs/request_log.txt"

# Container manager class to manage Containers
class ContainerManager:
  def __init__(self):
    self.containers = []
    self.next_port = INITIAL_PORT

  def start_container(self):
    name = f"assign1-{self.next_port}"
    port = self.next_port
    subprocess.run([
      "podman", "run", "-d",
      "--name", name,
      "-v", FOLDER_PATH,
      "-p", f"{port}:8080",
      CONTAINER_IMAGE
    ])
    self.containers.append((name, port))
    self.next_port += 1
    print(f"Container {name} started on {port}")

  def stop_last_container(self):
    if not self.containers:
        return
    name, _ = self.containers.pop()
    subprocess.run(["podman", "stop", name])
    subprocess.run(["podman", "rm", name])
    print(f"Stopped container {name}")

  def count(self):
    return len(self.containers)

# to monitor the container, if no requests in 30 seconds, stop the last container
# ------------------------ HELPERS ------------------------
def load_requests(path=REQUEST_LOG, window=10):
  now = time.time()
  try:
    with open(path, "r") as f:
      timestamps = [float(line.strip()) for line in f if line.strip()]
    return [t for t in timestamps if t >= now - window]
  except FileNotFoundError:
    return []

# Main function
def main(algo):
  manager = ContainerManager()
  afk_time = time.time()

  # start the container (2 containers for initial load)
  manager.start_container() 
  manager.start_container() 

  while True:
    if algo == 1:
      recent_requests = load_requests(window=5)
      pending = len(recent_requests)
      print(f"Pending requests in last 5s: {pending}")
      if pending > 5:
          manager.start_container()
      elif pending == 0 and time.time() - afk_time > 30:
        # remove extra containers with scaling algorithm
        while manager.count() > 2:
          manager.stop_last_container()

    elif algo == 2:
      rps = len(load_requests(window=10)) / 10
      print(f"Average RPS (10s window): {rps:.2f}")
      if rps > 3:
          manager.start_container()
      elif rps < 1 and len(load_requests(window=30)) < 1:
        # remove extra containers with scaling algorithm
        while manager.count() > 2:
          manager.stop_last_container()

    if len(load_requests()) == 0:
      afk_time = time.time()

    time.sleep(5)

# Requesting Arguments for scaling algo, default = 1 (rule-based scaling)
if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--algo", type=int, default=1, help="Scaling algorithm: 1=rule-based, 2=sliding avg")
  args = parser.parse_args()
  main(args.algo)
