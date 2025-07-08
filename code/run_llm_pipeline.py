import os
import json
import subprocess
import time

base_dir = os.path.expanduser("~/prost/testbed/benchmarks")
json_file = os.path.join(base_dir, "jsonfiles", "llm_tasks.json")
prost_testbed_dir = os.path.expanduser("~/prost/testbed")
prost_dir = os.path.expanduser("~/prost")

def run_command(command, output_file=None, cwd=None):
    with open(output_file, 'w') as outfile:
        process = subprocess.Popen(command, shell=True, cwd=cwd, stdout=outfile, stderr=subprocess.STDOUT)
    return process

with open(json_file, 'r') as f:
    tasks_data = json.load(f)
    tasks = tasks_data.get("tasks", [])

for task_name in tasks:
    safe_task_name = task_name.replace(" ", "_")
    instance_file = f"instance_{safe_task_name}.rddl"

    server_output_file = os.path.join(prost_testbed_dir, f"{safe_task_name}_plans.txt")
    instance_output_file = os.path.join(prost_testbed_dir, f"{safe_task_name}_time.txt")

    print(f"\nProcessing task: {task_name}")

    os.chdir(prost_testbed_dir)
    server_cmd = "./run-server.py -b benchmarks/generated_instances/"
    print(f"Running server: {server_cmd}")
    server_process = run_command(server_cmd, output_file=server_output_file)

    time.sleep(5)

    os.chdir(prost_dir)
    prost_cmd = f"./prost.py instance_{safe_task_name} \"[Prost -s 1 -se [IPC2014] -se [IPC2011]]\""
    print(f"Running planner: {prost_cmd}")
    prost_process = run_command(prost_cmd, output_file=instance_output_file)

    time.sleep(420)

    server_process.terminate()
    prost_process.terminate()

print("\nAll tasks completed successfully.")