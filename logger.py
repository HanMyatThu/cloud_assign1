import subprocess
import time
import csv
from datetime import datetime

LOG_FILE = "./logs/container_log.csv"
INTERVAL = 5 

def get_containers():
  try:
    result = subprocess.run([
      "podman", "ps", "--format", "{{.Names}}"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    lines = result.stdout.strip().split('\n')
    count = len([name for name in lines if name.startswith("assign1-")])
    return count

  except Exception as e:
    print(f"Error fetching container count: {e}")
    return 0


def log_container_count():
    with open(LOG_FILE, mode='w', newline='') as file:
      writer = csv.writer(file)
      writer.writerow(["timestamp", "datetime", "active_containers"])

      while True:
        count = get_containers()
        ts = time.time()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow([ts, now, count])
        file.flush()
        print(f"[{now}] Containers running: {count}")
        time.sleep(INTERVAL)


if __name__ == "__main__":
  log_container_count()
