import json
import re
import argparse

def update_rddl_rewards(json_file, task_name, rddl_file, output_file):
    with open(json_file, "r") as jf:
        data = json.load(jf)
    
    if task_name not in data["tasks"]:
        raise ValueError(f"Task '{task_name}' not found in the JSON file.")
    
    rewards = data["tasks"][task_name]["rewards"]
    reward_text = "\n        ".join(rewards) + "\n"
    
    with open(rddl_file, "r") as rf:
        rddl_content = rf.read()
    
    match = re.search(r"reward\s*=(.*?);", rddl_content, flags=re.DOTALL)
    if match:
        existing_text = match.group(1).strip()
        new_reward_section = f"reward = {reward_text}        {existing_text}\n;"
        updated_content = re.sub(r"reward\s*=.*?;", new_reward_section, rddl_content, flags=re.DOTALL)
    else:
        updated_content = rddl_content
    
    with open(output_file, "w") as of:
        of.write(updated_content)
    
    print(f"Updated RDDL domain file saved as {output_file} : rewards")

def update_non_fluent(json_file, task_name, rddl_file, domain_output, instance_file, instance_output, nf_string=""):
    with open(json_file, "r") as jf:
        data = json.load(jf)
    if task_name not in data["tasks"]:
        raise ValueError(f"Task '{task_name}' not found in the JSON file.")
    goals = data["tasks"][task_name].get(nf_string, [])
    
    # Modify the non-fluents section while preserving existing text
    goal_text = "\n        " + "\n        ".join(goals) + "\n" 
    with open(instance_file, "r") as rf:
        instance_content = rf.read()  
    match = re.search(r"non-fluents\s*{(.*?)}", instance_content, flags=re.DOTALL)
    if match:
        new_non_fluents = f"non-fluents {{{goal_text}{match.group(1)}}}"
        updated_content = instance_content.replace(match.group(0), new_non_fluents)
    else:
        updated_content = instance_content
    
    with open(instance_output, "w") as of:
        of.write(updated_content)
    print(f"Updated instance RDDL file saved as {instance_output}")

    # Modify the pvariables section while preserving existing text
    if nf_string == "goal":
        goal_variables = [f"GOAL_{i}(item, item, location) : {{ non-fluent, bool, default = false }};" for i in range(len(goals))]
    elif  nf_string == "destination":
        goal_variables = [f"DESTINATION_{i}(item, location) : {{ non-fluent, bool, default = false }};" for i in range(len(goals))]
    else:
        goal_variables = []

    goal_text = "\n        " + "\n        ".join(goal_variables) + "\n"  

    with open(rddl_file, "r") as rf:
        rddl_content = rf.read()
    
    match = re.search(r"(pvariables\s*{)", rddl_content)
    if match:
        start_index = match.end()  # Position after "pvariables {"
        updated_content = rddl_content[:start_index] + goal_text + rddl_content[start_index:]
    else:
        updated_content = rddl_content
    
    with open(domain_output, "w") as of:
        of.write(updated_content)
    print(f"Updated domain RDDL file saved as {domain_output} pvariables:{nf_string}")

def add_instance_objects(json_file, task_name, instance_file, instance_output):
    with open(json_file, "r") as jf:
        data = json.load(jf)

    if task_name not in data["tasks"]:
        raise ValueError(f"Task '{task_name}' not found in the JSON file.")

    new_items = set(data["tasks"][task_name].get("items", []))
    new_locations = set(data["tasks"][task_name].get("locations", []))

    with open(instance_file, "r") as rf:
        instance_content = rf.read()

    # Update locations
    location_match = re.search(r"(location\s*:\s*{)([^}]*)}", instance_content)
    if location_match:
        existing_locations = set(map(str.strip, location_match.group(2).split(",")))
        existing_locations.discard("")  # Remove empty entries
        updated_locations = existing_locations | new_locations
        updated_locations_str = ", ".join(sorted(updated_locations))

        instance_content = re.sub(
            r"(location\s*:\s*{)[^}]*}",
            rf"\1 {updated_locations_str} }}",
            instance_content
        )

    # Update items
    item_match = re.search(r"(item\s*:\s*{)([^}]*)}", instance_content)
    if item_match:
        existing_items = set(map(str.strip, item_match.group(2).split(",")))
        existing_items.discard("")
        updated_items = existing_items | new_items
        updated_items_str = ", ".join(sorted(updated_items))

        instance_content = re.sub(
            r"(item\s*:\s*{)[^}]*}",
            rf"\1 {updated_items_str} }}",
            instance_content
        )

    with open(instance_output, "w") as of:
        of.write(instance_content)
    print(f"Update RDDL instance file saved as {instance_output}: items and locations")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to update rewards, non-fluents and objects in a RDDL base domain and instance for a particular task. \
                                     Run once.")
    parser.add_argument("task_name", type=str, help="The name of the task to update.", default="prepare food", nargs="?")
    args = parser.parse_args()

    json_file = "jsonfiles/minimum_types.json"
    task_name = args.task_name
    
    rddl_file = "rddl/test.rddl" # base_domain
    output_file = "rddl/test.rddl" # change to task name
    instance_file = "rddl/test_instance.rddl" # base_instance
    output_instance = "rddl/test_instance.rddl" # change to task name

    update_rddl_rewards(json_file, task_name, rddl_file, output_file)
    update_non_fluent(json_file, task_name, rddl_file, output_file, instance_file, output_instance, "goal")
    update_non_fluent(json_file, task_name, rddl_file, output_file, instance_file, output_instance, "destination")
    add_instance_objects(json_file, task_name, instance_file, output_instance)
