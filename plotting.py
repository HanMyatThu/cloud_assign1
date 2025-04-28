import pandas as pd
import matplotlib.pyplot as plt

test_cases = {
    'RR + Algo1': {
        'container_log': 'logs/1/container_log_rr_algo1.csv',
        'detailed_log': 'logs/1/detailed_log_rr_algo1.csv'
    },
    'RR + Algo2': {
        'container_log': 'logs/rr_algo2/container_log_rr_algo2.csv',
        'detailed_log': 'logs/rr_algo2/detailed_log_rr_algo2.csv'
    },
    'State + Algo1': {
        'container_log': 'logs/state_algo1/container_log_state_algo1.csv',
        'detailed_log': 'logs/state_algo1/detailed_log_state_algo1.csv'
    },
    'State + Algo2': {
        'container_log': 'logs/state_algo2/container_log_state_algo2.csv',
        'detailed_log': 'logs/state_algo2/detailed_log_state_algo2.csv'
    }
}

colors = ['#4E79A7', '#59A14F', '#E15759', '#79706E']

max_containers = {}
total_durations = {}
average_response_times = {}

# Analyze each case
for label, files in test_cases.items():
    # container log
    cont_df = pd.read_csv(files['container_log'], header=None)
    cont_df.columns = ['timestamp', 'container_name', 'active_containers']
    cont_df['active_containers'] = pd.to_numeric(cont_df['active_containers'], errors='coerce')

    #get max active containers
    max_containers[label] = cont_df['active_containers'].max()

    # detailed log
    req_df = pd.read_csv(files['detailed_log'], header=None)
    req_df.columns = ['timestamp', 'container_url', 'response_time', 'status_code']
    req_df['timestamp'] = pd.to_numeric(req_df['timestamp'], errors='coerce')
    req_df['response_time'] = pd.to_numeric(req_df['response_time'], errors='coerce')

    # Calculate total duration (max - min timestamp)
    total_durations[label] = req_df['timestamp'].max() - req_df['timestamp'].min()

    # Calculate average response time
    average_response_times[label] = req_df['response_time'].mean()

# Plot Max Containers Comparison
plt.figure(figsize=(10,6))
plt.bar(max_containers.keys(), max_containers.values(), color=colors)
plt.ylabel('Max Number of Containers')
plt.title('Comparison of Max Containers Required')
plt.grid(axis='y')
plt.xticks(rotation=30, ha='right')
plt.tight_layout()
plt.savefig('comparison_max_containers.png')
plt.show()

# Plot Total Duration Comparison
plt.figure(figsize=(10,6))
plt.bar(total_durations.keys(), total_durations.values(), color=colors)
plt.ylabel('Total Duration (seconds)')
plt.title('Comparison of Total Processing Time')
plt.grid(axis='y')
plt.xticks(rotation=30, ha='right')
plt.tight_layout()
plt.savefig('comparison_total_duration.png')
plt.show()

# Plot Average Response Time Comparison
plt.figure(figsize=(10,6))
plt.bar(average_response_times.keys(), [v*1000 for v in average_response_times.values()], color=colors)
plt.ylabel('Average Response Time (ms)')
plt.title('Comparison of Average Response Times')
plt.grid(axis='y')
plt.xticks(rotation=30, ha='right')
plt.tight_layout()
plt.savefig('comparison_avg_response_time.png')
plt.show()

print("Done!")