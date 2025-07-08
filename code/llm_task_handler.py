import json
import os
from dotenv import load_dotenv
from groq import Groq
from datetime import datetime


load_dotenv()

GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Set up directory path
cur_dir = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(cur_dir, "jsonfiles", "master_tasks.json"), "r") as f:
    master_tasks = json.load(f)

# Load JSON data
jsonfiles = ["sequence.json", "virtualhome_categories.json"]
data = {}
for file in jsonfiles:
    with open(os.path.join(cur_dir, "jsonfiles", file), "r") as f:
        data[file.split(".")[0]] = json.load(f)

# Determine the time of day
def get_time_of_day():
    hour = datetime.now().hour
    if 5 <= hour < 11:
        return "morning"
    elif 11 <= hour < 18:
        return "afternoon"
    elif 18 <= hour < 22:
        return "evening"
    else:
        return "night"

# Task prompt template
def generate_prompt(user_task, sequences, kitchen_info):
    time_of_day = get_time_of_day()
    
    return f"""
    # The following tasks are possible in the household:
    tasks_sample_space = {master_tasks["tasks"]}
    
    # The following tasks were done previously:
    user_tasks = {sequences}
    
    # Kitchen-related information:
    kitchen_receptacles = {kitchen_info["Items"]}
    kitchen_objects = {kitchen_info["Appliances"]}
    rooms = {kitchen_info["Rooms"]},
    furniture = {kitchen_info["Furniture"]},
    kitchen_food = {kitchen_info["Food"]}

    # Current time of day: {time_of_day} or according to {user_task}
    Avoid predicting breakfast options unless it is morning.
    
    {user_task}

    Answer only as a valid Python dictionary with a key: 'tasks'.
    The number of tasks should be 4 and must be from the sample space.
    """

# LLM prompt function
def prompt_model(task):
    prompt = generate_prompt(task, data["sequence"], data["virtualhome_categories"])
    client = Groq(api_key=GROQ_API_KEY)
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are an AI assistant that provides household task predictions based on user activity and time of day."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )
    
    output_text = response.choices[0].message.content
    return eval(output_text[output_text.find('{'):output_text.rfind('}')+1])

# Validate response against master task list
def validate_tasks(task_list):
    for task in task_list:
        if task not in master_tasks["tasks"]:
            return False, f"Invalid task detected: {task}. Replace with a valid task."
    return True, ""

# Main function
def main():
    user_task = input(f'What do you want to do? ').strip().lower()
    response_dict = prompt_model(user_task)
    tasks = response_dict.get("tasks", [])
    
    is_valid, feedback = validate_tasks(tasks)
    
    while not is_valid:
        print(f"Feedback: {feedback}")
        response_dict = prompt_model(feedback)
        tasks = response_dict.get("tasks", [])
        is_valid, feedback = validate_tasks(tasks)
    
    output_file = os.path.join(cur_dir, "jsonfiles", "llm_tasks.json")
    with open(output_file, "w") as f:
        json.dump(response_dict, f, indent=4)
    
    print("Final Tasks:", response_dict)

if __name__ == "__main__":
    main()
