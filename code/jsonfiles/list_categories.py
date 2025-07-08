import json
from simulation.unity_simulator import comm_unity

# Initialize VirtualHome Unity Communication
comm = comm_unity.UnityCommunication()

# Reset environment (ensures a fresh start)
comm.reset()

# Get the environment graph (contains objects and their categories)
success, env_graph = comm.environment_graph()

if not success:
    print("Failed to retrieve environment graph. Ensure Unity simulator is running.")
    exit()

# Dictionary to store categories and objects
categories_dict = {}

# Iterate over objects in the environment
for obj in env_graph["nodes"]:
    if "category" in obj and "class_name" in obj:
        category = obj["category"]
        class_name = obj["class_name"]
        
        # Group objects by their categories
        if category not in categories_dict:
            categories_dict[category] = []
        categories_dict[category].append(class_name)

# Print categories and their objects
for category, objects in categories_dict.items():
    print(f"\n Category: {category.capitalize()}")
    print(", ".join(objects))

# Save categories and objects to a JSON file
output_data = {
    "_comment": "This file contains object categories from VirtualHome. Each category lists the objects belonging to it.",
    "categories": categories_dict
}

with open("virtualhome_categories.json", "w") as f:
    json.dump(output_data, f, indent=4)

print("\n Categories and objects saved to 'virtualhome_categories.json'")
