import sys
import os
import json
import numpy as np

def load_tasks(filename="./jsonfiles/success_paths.json"):
    with open(filename, "r") as file:
        return json.load(file)

def check_noise_threshold():
    noise_samples = np.abs(np.random.normal(0, 0.1, 10))  # Generate 10 positive noise samples
    noise_range = (np.min(noise_samples), np.max(noise_samples))
    threshold = np.mean(noise_samples) + np.std(noise_samples) * 0.5  # Dynamic threshold
    noise_value = np.random.choice(noise_samples) 
    print(f"Noise Value: {noise_value:.3f}, Noise Range: {noise_range}, Threshold: {threshold:.3f}")
    return noise_value <= threshold

def process_task(task_name, actions):
    results = []
    for i in range(10):  # Run for 10 iterations per task
        new_script = [action for action in actions if check_noise_threshold()]
        results.append(f"Iteration {i+1}:\n" + "\n".join(new_script) + "\n\n")
    return results

def main():
    tasks = load_tasks()
    with open("output_log_all_tasks.txt", "w") as output_file:
        for task_name, actions in tasks.items():
            output_file.write(f"Task: {task_name}\n")
            output_file.writelines(process_task(task_name, actions))
            output_file.write("\n")
            print(f"Completed 10 iterations for task: {task_name}\n")

if __name__ == "__main__":
    main()