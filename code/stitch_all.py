import os
import subprocess
import json
import shutil

def run_command(command):
    """Run a shell command and return output."""
    with subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            print(f"Error running command: {command}\n{stderr}")
        return stdout

def main():
    benchmarks_dir = "prost/testbed/benchmarks/generated_instances"
    os.chdir("prost/testbed")
    
    # Start the server and capture output
    server_output_file = "server_output.txt"
    server_command = f"./run-server.py -b {benchmarks_dir} > {server_output_file} &"
    run_command(server_command)
    
    # Run Prost for all instances
    instances = [f for f in os.listdir(benchmarks_dir) if f.startswith("instance_")]
    os.makedirs("top_rounds", exist_ok=True)
    
    # Wait for server to generate outputs
    print("Waiting for server to complete processing...")
    subprocess.run(["sleep", "10"])  # Adjust as needed
    
    for instance in instances:
        task_name = instance.replace("instance_", "").split(".")[0]
        
        # Parse the server output for this task
        plan_output_file = server_output_file
        top_rounds_json = f"top_rounds/{task_name}.json"
        parse_command = f"python3 ../../plan_parser.py --file {plan_output_file}"
        run_command(parse_command)
        
        # Move JSON output to structured folder
        if os.path.exists("top_rounds.json"):
            shutil.move("top_rounds.json", top_rounds_json)
            print(f"Saved: {top_rounds_json}")
    
    print("All instances processed successfully!")
    
if __name__ == "__main__":
    main()
