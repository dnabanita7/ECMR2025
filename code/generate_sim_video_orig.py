import sys
import os
import json
import numpy as np

sys.path.append('../virtualhome-2.3.0/simulation/')
from simulation.unity_simulator.comm_unity import UnityCommunication


llm_tasks_path = os.path.expanduser("~/IROS25/jsonfiles/llm_tasks.json")
task_scripts_path = os.path.expanduser("~/IROS25/jsonfiles/task_scripts.json")


with open(llm_tasks_path, "r") as file:
    llm_tasks = json.load(file)

with open(task_scripts_path, "r") as file:
    task_scripts = json.load(file)


mapped_tasks = {
    task: task_scripts[task] for task in llm_tasks["tasks"] if task in task_scripts
}

for task, actions in mapped_tasks.items():
    print(f"Task: {task}")
    for action in actions:
        print(f"  - {action}")
    print()

#print(mapped_tasks)
# print(mapped_tasks[llm_tasks["tasks"][0]])
#------------------------xxxx to be updated xxxx---------------------------------------


print('Starting Unity...')
comm = UnityCommunication()

print('Starting scene...')
comm.reset(0)
comm.add_character('Chars/Male2')

s, graph = comm.environment_graph()

cereal = [node['id'] for node in graph['nodes'] if node['class_name'] == 'cereal'][0]
print(cereal)

dishbowl = [node['id'] for node in graph['nodes'] if node['class_name'] == 'dishbowl'][0]
print(dishbowl)

def check_noise_threshold():
    noise_samples = np.abs(np.random.normal(0, 0.1, 10))  # Generate 10 positive noise samples
    noise_range = (np.min(noise_samples), np.max(noise_samples))
    threshold = np.mean(noise_samples) + np.std(noise_samples) * 0.5  # Dynamic threshold
    noise_value = np.random.choice(noise_samples) 
    print(f"Noise Value: {noise_value:.3f}, Noise Range: {noise_range}, Threshold: {threshold:.3f}")
    return noise_value <= threshold  


# script = [ f'<char0> [walk] <kitchen> (1)',
#             '<char0> [find] <cereal> ({})'.format(cereal),
#             '<char0> [grab] <cereal> ({})'.format(cereal),
#             '<char0> [walktowards] <dishbowl> ({})'.format(dishbowl),
#             '<char0> [putback] <cereal> ({}) <dishbowl> ({})'.format(cereal, dishbowl),
#          ]

script = [ f"<char0> [walk] <kitchen> (1)",
            "<char0> [grab] <cereal> ({})".format(cereal),
            "<char0> [putin] <cereal> ({}) <dishbowl> ({})".format(cereal, dishbowl),
    ]

def main():
    new_script = [action for action in script if check_noise_threshold()]

    print('New script:', new_script)

    print('Rendering script...')
    comm.render_script(new_script, recording=True, find_solution=True, camera_mode=['PERSON_FROM_BACK'])

    print('Generated, find video in simulation/unity_simulator/output/')

if __name__ == "__main__":
    for _ in range(10):  # Run for 10 iterations
        main()
        print("\n")

