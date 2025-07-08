import json
import numpy as np



saved_stats = {}

def load_json(file_name):
    with open(file_name) as f:
        data = json.load(f)
    return data

with open('../jsonfiles/master_tasks.json') as f:
    master_tasks = json.load(f)

task_names = master_tasks['tasks']  # Assuming it's a list
task_names = [task.replace(" ", "_").lower() for task in task_names]
print(task_names)


for task_name in task_names:
    data_wo_human = load_json(f'{task_name}_wo_human.json')
    baseline_sum = data_wo_human['round_1']['reward'] + data_wo_human['round_2']['reward'] + data_wo_human['round_3']['reward']
    
    data = load_json(f'{task_name}.json')
    ours_sum = data['round_1']['reward'] + data['round_2']['reward'] + data['round_3']['reward']

    avg_ours = ours_sum / 3
    avg_baseline = baseline_sum / 3

    arr_ours = np.array([data['round_1']['reward'], data['round_2']['reward'], data['round_3']['reward']])
    arr_baseline = np.array([data_wo_human['round_1']['reward'], data_wo_human['round_2']['reward'], data_wo_human['round_3']['reward']])

    std_dev_ours = np.std(arr_ours, ddof=0)
    std_dev_baseline = np.std(arr_baseline, ddof=0)

    # print("Baseline: ", avg_baseline, std_dev_baseline)
    # print("Ours: ", avg_ours, std_dev_ours)

    diff_avg = avg_ours - avg_baseline
    diff_std_dev = np.sqrt(std_dev_baseline**2 + std_dev_ours**2)

    # print("Difference in average: ", diff_avg)
    # print("Difference in std dev: ", diff_std_dev)

    saved_stats[f"{task_name}"] = {
    "baseline_avg": np.round(avg_baseline, 2),
    "baseline_std_dev": np.round(std_dev_baseline, 2),
    "ours_avg": np.round(avg_ours, 2),
    "ours_std_dev": np.round(std_dev_ours, 2),
    "diff_avg": np.round(diff_avg, 2),
    "diff_std_dev": np.round(diff_std_dev, 2)
    }

saved_stats = json.dumps(saved_stats, indent=4)
with open('saved_stats.json', 'w') as f:
    f.write(saved_stats)
