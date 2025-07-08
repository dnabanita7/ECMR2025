import json
import os
import sys

def convert_action(action):
    mapping = {
        "move": "walk",
        "move_human": "walk",
        "pick": "grab",
        "pick_human": "grab",
        "place": "put",
        "place_human": "put",
        "clean": "walkforward", #imitate cleaning
        "clean_human": "walkforward",
        "put_in": "putin",
        "put_in_human": "putin",
        "agent_switch_on": "switchon",
        "agent_switch_off": "switchoff",
        "human_switch_on": "switchon",
        "human_switch_off": "switchoff",
        "agent_open": "open",
        "agent_close": "close",
        "human_open": "open",
        "human_close": "close"
    }
    
    action = action.strip("[];" )  # Remove brackets and semicolons
    actions = action.split(";, ") if ";," in action else [action]  # Handle single/multiple actions
    converted_actions = []
    
    for act in actions:
        act_parts = act.split("(")
        if len(act_parts) < 2:
            continue  # Skip invalid actions
        
        action_name = act_parts[0].strip()
        params = act_parts[1].strip(")").split(", ")
        
        if len(params) < 1:
            continue  # Skip invalid actions
        
        actor = "<char1>" if "human" in params[0] else "<char0>"
        verb = mapping.get(action_name, action_name)
        
        if verb == "walk" and len(params) > 1:
            converted_actions.append(f"{actor} [walk] <{params[2]}> (4)")
        elif verb == "walkforward" and len(params) > 1:
            converted_actions.append(f"{actor} [walkforward] (4)")
        elif verb == "grab" and len(params) > 1:
            converted_actions.append(f"{actor} [grab] <{params[1]}> (2)")
        elif verb in ["put", "putin"] and len(params) > 1:
            converted_actions.append(f"{actor} [{verb}] <{params[1]}> (2) <{params[2]}> (2)")
        elif verb == "walktowards" and len(params) > 0:
            converted_actions.append(f"{actor} [walktowards] <{params[1]}> (3)")
        elif verb in ["open", "close", "switchon", "switchoff"] and len(params) > 0:
            converted_actions.append(f"{actor} [{verb}] <{params[1]}> (2)")
    
    return " | ".join(converted_actions) if len(converted_actions) > 1 else "\n".join(converted_actions)

def convert_json_to_virtualhome(json_data):
    virtualhome_scripts = []
    for round_key, round_value in json_data.items():
        actions = round_value.get("actions", [])
        converted_actions = [convert_action(action) for action in actions if action.strip()]
        virtualhome_scripts.append({"round": round_key, "script": converted_actions})
    return virtualhome_scripts

def main(input_folder):
    output_folder = os.path.join(input_folder, "converted")
    os.makedirs(output_folder, exist_ok=True)  # Create output folder if it doesn't exist

    # Get sorted list of JSON files
    json_files = sorted([f for f in os.listdir(input_folder) if f.endswith(".json")])

    for filename in json_files:
        input_file = os.path.join(input_folder, filename)
        output_file = os.path.join(output_folder, os.path.splitext(filename)[0] + "_virtualhome.json")

        with open(input_file, "r") as f:
            json_data = json.load(f)

        virtualhome_scripts = convert_json_to_virtualhome(json_data)

        with open(output_file, "w") as f:
            json.dump(virtualhome_scripts, f, indent=4)

        print(f"Converted: {filename} -> {output_file}")

if __name__ == "__main__":
    folder_path = "./rddl_text_plans/"
    main(folder_path)

# TO-DO: 
# char 0 agent
# handling duplicates and dropping of objects
