import json
import os
import random

def generate_domain_file(task_name, base_domain_path, destinations, goals, rewards, output_dir):
    """Generates a modified RDDL domain file with updated task-specific parameters and rewards."""
    
    with open(base_domain_path, "r") as file:
        domain_content = file.read()

    new_domain_name = f"domain_x_robot_anticipation_{task_name}"
    domain_content = domain_content.replace("domain_x_robot_anticipation", new_domain_name, 1)

    pvariables_start = domain_content.find("pvariables {")
    cpfs_start = domain_content.find("cpfs {")

 
    pvariables_end = domain_content.rfind("};", pvariables_start, cpfs_start) + 2 

    existing_pvariables = domain_content[pvariables_start:pvariables_end]

    new_non_fluents = []
    if destinations:
        new_non_fluents += [f"DESTINATION_{i}(item, location) : {{ non-fluent, bool, default = false }};" for i in range(len(destinations))]
    if goals:
        new_non_fluents += [f"GOAL_{i}(item, item, location) : {{ non-fluent, bool, default = false }};" for i in range(len(goals))]

    # Insert new non-fluents before `};`
    updated_pvariables = existing_pvariables[:-2] + "\n    " + "\n    ".join(new_non_fluents) + "\n};"

    # Replace the old `pvariables` block with the updated one
    domain_content = domain_content[:pvariables_start] + updated_pvariables + domain_content[pvariables_end:]


    # Extract and update reward expression
    reward_marker = "reward ="
    reward_start = domain_content.find(reward_marker)

    if reward_start != -1:
        reward_end = domain_content.find(";", reward_start)
        existing_rewards = domain_content[reward_start + len(reward_marker):reward_end].strip()
        cleaned_rewards = existing_rewards.split() if existing_rewards else []
    else:
        cleaned_rewards = []

    new_rewards_list = [r for r in rewards]

    updated_rewards = cleaned_rewards + new_rewards_list
    updated_reward_expression = f"{reward_marker} {' '.join(updated_rewards)};"

    if reward_start != -1:
        domain_content = domain_content[:reward_start] + updated_reward_expression + domain_content[reward_end + 1:]
    else:
        domain_content += f"\n{updated_reward_expression}"


    # Save the updated domain file
    output_path = os.path.join(output_dir, f"{new_domain_name}.rddl")
    with open(output_path, "w") as file:
        file.write(domain_content)

    print(f"Generated domain file: {output_path}")

  

def generate_duplicate_instances(task_name, items):
    new_items = list(items)
    equal_items = list()

    for item in items:
        if item in ['dishbowl', 'plate', 'glass']:
            equal_items.append((f"{item}", f"{item}_1"))
            new_items.append(f"{item}_1")
    return list(equal_items), new_items

def generate_instance(task_name, items, locations, destination, goals, output_dir):
    # Ensure broom and mop are always included
    equal_items, new_items = generate_duplicate_instances(task_name, items)
    if random.random() < 0.5 :
        clean_item = ['broom']
    else:
        clean_item = ['mop']
    items = set(new_items + clean_item)
    
    # Generate COST definitions dynamically based on locations
    cost_definitions = []
    for loc1 in locations:
        for loc2 in locations:
            cost = 0 if loc1 == loc2 else random.randint(10, 20)
            cost_definitions.append(f"COST(robot, {loc1}, {loc2}) = {cost};")
    
    # Assign agent and human locations
    agent_location = locations[0]
    human_location = locations[-1]
    
    # Define attributes for items
    fragile_items = {item for item in items if item in ["plate", "glass", "waterglass", "waterglass_1", "dishbowl", "plate_1", "glass_1", "dishbowl_1"]}
    food_items = {item for item in items if item in ["apple", "cereal", "bread", "breadslice", "pizza-base", "salmon", "water", "banana", "coffee", "milk", "juice", "eggs"]}
    mop_items = {item for item in items if item in ["mop", "broom", "washingsponge"]}
    container_items = {item for item in items if item in ["plate", "glass", "dishbowl", "plate_1", "glass_1", "dishbowl_1", "waterglass", "pan", "mug"]}
    equal_items = set(equal_items)
    appliance_items = {loc for loc in locations if loc in ["cabinet", "stove", "fridge", "microwave", "oven", "toaster", "coffeemaker", "faucet", "sink", "garbagecan"]}
    has_switch_items = {loc for loc in locations if loc in ["stove", "microwave", "oven", "toaster", "coffeemaker", "faucet", "sink"]}


    # Determine object locations
    object_locations = []

    if "water" in items and "sink" in locations:
        object_locations.append("obj-loc(water, sink) = true;")
    if "water" in items and "faucet" in locations:
        object_locations.append("obj-loc(water, faucet) = true;")
    
    if "closet" in locations:
        object_locations.append("\n".join([f"obj-loc({item}, closet) = true;" for item in items if item in ["clothesshirt", "clothespant"]]))

    #if "fridge" in locations:
    #    object_locations.append("\n".join([f"obj-loc({item}, fridge) = true;" for item in items if item in ["eggs", "milk", "juice"]]))

    if "kitchencounter" in locations:
        object_locations.append("\n".join([f"obj-loc({item}, kitchencounter) = true;" for item in items if item not in ["water", "broom", "mop", "clothesshirt", "clothespant"]]))

    elif "bathroomcounter" in locations:
        object_locations.append("\n".join([f"obj-loc({item}, bathroomcounter) = true;" for item in items if item not in ["water", "broom", "mop", "eggs", "milk", "juice", "clothesshirt", "clothespant"]]))

    elif "cabinet" in locations:
        object_locations.append("\n".join([f"obj-loc({item}, cabinet) = true;" for item in items if item not in ["water", "broom", "mop", "eggs", "milk", "juice", "clothesshirt", "clothespant"]]))

    instance_template = f"""
non-fluents nf_instance_{task_name}_inst {{
    domain = domain_x_robot_anticipation_{task_name};

    // Objects in the domain
    objects {{
        location : {{{', '.join(locations)}}};
        item : {{{', '.join(items)}}};
        agent : {{robot}};
        human : {{human}};
    }};

    non-fluents {{
        {chr(10).join(cost_definitions)}
        {chr(10).join([f'FRAGILE({item}) = true;' for item in fragile_items])}
        {chr(10).join([f'FOOD_ITEM({item}) = true;' for item in food_items])}
        {chr(10).join([f'MOP_ITEM({item}) = true;' for item in clean_item])}
        {chr(10).join([f'CONTAINER({item}) = true;' for item in container_items])}
        {chr(10).join([f'EQUAL({pair[0]}, {pair[1]}) = true;' for pair in equal_items])}
        {chr(10).join([f'APPLIANCE({loc}) = true;' for loc in appliance_items])}
        {chr(10).join([f'HAS-SWITCH({loc}) = true;' for loc in has_switch_items])}
        {chr(10).join(goal for goal in goals)}
        {chr(10).join(dest for dest in destination)}

    }};
}}

instance instance_{task_name} {{
    domain = domain_x_robot_anticipation_{task_name};
    non-fluents = nf_instance_{task_name}_inst;

    init-state {{
        agent-loc(robot, {agent_location}) = true;
        human-loc(human, {human_location}) = true;

        obj-loc({clean_item[0]}, cabinet) = true;

        {chr(10).join(object_locations)}
    }};

    max-nondef-actions = 1;
    horizon = 35;
    discount = 1.0;
}}
    """
    
    # Write instance file
    file_path = os.path.join(output_dir, f"instance_{task_name}.rddl")
    with open(file_path, "w") as f:
        f.write(instance_template)
    print(f"Generated: {file_path}")

def main():
    input_file = "jsonfiles/rddl_goals.json"
    output_dir = "generated_instances"
    os.makedirs(output_dir, exist_ok=True)
    
    with open(input_file, "r") as f:
        task_data = json.load(f)
    
    for task_name, data in task_data["tasks"].items():
        generate_instance(task_name.replace(" ", "_"), data["items"], data["locations"], data["destination"], data["goal"], output_dir)
        base_domain_path = "rddl/domain_x_robot_anticipation.rddl"
        generate_domain_file(task_name.replace(" ", "_"), base_domain_path, data["destination"], data["goal"], data["rewards"], output_dir)

if __name__ == "__main__":
    main()
