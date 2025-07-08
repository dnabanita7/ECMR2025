# import json
# import os

# cur_dir = os.path.dirname(os.path.abspath(__file__))


# def goal_mapping():

#     with open(cur_dir+"/jsonfiles/minimum_types.json","r") as tasks:
#         all_tasks = json.load(tasks)
#     tasks.close()
    
#     with open(cur_dir+"/jsonfiles/llm_tasks.json","r") as goals:
#         rddl_goals = json.load(goals)
#         with open(cur_dir+"/rddl/rddl_goals.txt","w") as writing_goals:
#             for i in range(len(rddl_goals['tasks'])):
#                 writing_goals.write(f"task_{i}:{rddl_goals['tasks'][i]}")
#                 writing_goals.write("\n")
        
# if __name__ == '__main__':
#     goal_mapping()

import json


with open("jsonfiles/llm_tasks.json", "r") as file:
    tasks_to_extract = set(json.load(file).get("tasks", []))

with open("jsonfiles/minimum_types.json", "r") as file:
    all_tasks = json.load(file).get("tasks", {})

filtered_tasks = {task: all_tasks[task] for task in tasks_to_extract if task in all_tasks}

with open("jsonfiles/rddl_goals.json", "w") as file:
    json.dump({"tasks": filtered_tasks}, file, indent=4)

print("Filtered tasks have been saved to rddl_goals.json")

