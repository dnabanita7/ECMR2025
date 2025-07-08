import json
from datetime import datetime
from pathlib import Path
import re
import ast
from groq import Groq

# task_description = {
#     "Prepare Food": 
#     {
#         "task_description": "Goal is to serve a apple in a plate, on the coffeetable.",
#         "scene_description": "robot is at kitchencounter, human is at cabinet, mop is in cabinet, \
#                               plate,plate_1, dishbowl,dishbowl_1, apple are at kitchencounter."
#     },
#     "Prepare Cereal":
#     {
#         "task_description": "Goal is to prepare a bowl of cereal and mug of milk, on the kitchencounter.",
#         "scene_description": "robot is at kitchencounter, human is at cabinet, mop is in cabinet, \
#                               mug, dishbowl,dishbowl_1, cereal, milk are at kitchencounter."
#     },
#     "Prepare Toast":
#     {
#         "task_description": "Goal is to serve a toasted breadslice in a plate, on the coffeetable.",
#         "scene_description": "robot is at kitchencounter, human is at cabinet, mop is in cabinet, \
#                               plate, plate_1, breadslice are at kitchencounter."
#     },
#     "Prepare Salmon":
#     {
#         "task_description": "Goal is to serve a cooked salmon in a plate, on the coffeetable.",
#         "scene_description": "robot is at kitchencounter, human is at cabinet, mop is in cabinet, \
#                               plate,plate_1, salmon are at kitchencounter."
#     },
#     "Serve Cereal":
#     {
#         "task_description": "Goal is to serve a bowl of cereal and mug of milk, on the coffeetable.",
#         "scene_description": "robot is at kitchencounter, human is at cabinet, mop is in cabinet, \
#                               mug, dishbowl,dishbowl_1, cereal, milk are at kitchencounter."

#     },
#     "Serve Water":
#     {
#         "task_description": "Goal is to serve a glass of water, on the coffeetable.",
#         "scene_description": "robot is at coffeetable, human is at faucet, mop is in cabinet, \
#                               waterglass, waterglass_1 are at kitchencounter, water at faucet."
#     },
#     "Serve Coffee":
#     {
#         "task_description": "Goal is to serve a glass of prepared coffee, on the coffeetable.",
#         "scene_description": "robot is at cabinet, human is at faucet, mop is in cabinet, \
#                               pan, glass, glass_1, coffee are at cabinet, water at faucet."

#     },
#     "Serve Pizza":
#     {
#         "task_description": "Goal is to serve a plate of baked pizzabase, on the coffeetable.",
#         "scene_description": "robot is at cabinet, human is at microwave, mop is in cabinet, \
#                               plate, plate_1, pizza-base are at cabinet."
#     },
#     "Serve Eggs":
#     {
#         "task_description": "Goal is to serve a plate of boiled eggs, on the kitchencounter.",
#         "scene_description": "robot is at sink, human is at cabinet, mop is in cabinet, \
#                               eggs, pan, plate, plate_1, pizza-base are at cabinet, water is at sink."

#     },
#     "Serve Fruits":
#     {
#         "task_description": "Goal is to serve a dishbowl of apple, banana with knife, on the coffetable.",
#         "scene_description": "robot is at kitchencounter, human is at cabinet, mop is in cabinet, \
#                               dishbowl, dishbowl_1, knife, apple, banana, plate, plate_1 are at cabinet."

#     },
#     "Wash Dishes":
#     {
#         "task_description": "Goal is to clean plates at sink.",
#         "scene_description": "robot is at sink, human is at faucet, mop is in cabinet, \
#                               soap, washingsponge, plate, plate_1 are at cabinet."

#     }
# }

# description of task in natural language, actions are there, constants in instance file: <location>, <item>
task_description = {
    "Prepare Food": 
    {
        "task_description": "Goal is to serve a apple in a plate, on the coffeetable.",
    },
    "Prepare Cereal":
    {
        "task_description": "Goal is to prepare a bowl of cereal and mug of milk, on the kitchencounter.",
    },
    "Prepare Toast":
    {
        "task_description": "Goal is to serve a toasted breadslice in a plate, on the kitchencounter.",
    },
    "Prepare Salmon":
    {
        "task_description": "Goal is to serve a cooked salmon in a plate, on the coffeetable.",
    },
    "Serve Cereal":
    {
        "task_description": "Goal is to serve a dishbowl of cereal and mug of milk, on the coffeetable.",
    },
    "Serve Water":
    {
        "task_description": "Goal is to serve a glass of water, at the coffeetable.",
    },
    "Serve Coffee":
    {
        "task_description": "Goal is to serve a glass of coffee on the coffeetable, prepared at coffeemaker location, with coffee and water in a glass and coffeemaker switched on.",
    },
    "Serve Pizza":
    {
        "task_description": "Goal is to serve a plate of baked pizzabase, at the coffeetable. To bake it we \"place\" the pizzabase at oven/microwave location which is switched on. We then serve this baked pizza base in a plate at coffeetable.",
    },
    "Serve Eggs":
    {
        "task_description": "Goal is to serve a plate of boiled eggs, on the kitchencounter.",
    },
    "Serve Fruits":
    {
        "task_description": "Goal is to serve a dishbowl of apple, banana with knife, on the coffetable.",
    },
    "Wash Dishes":
    {
        "task_description": "Goal is to \"place\" a plate with soap and washingsponge at sink and switch on water from faucet.",
    }
}

scene_description = {
    "dishbowl": "kitchencounter",
    "dishbowl_1": "kitchencounter",
    "milk": "kitchencounter",
    "cereal": "kitchencounter",
    "mop" : "cabinet",
    "mug": "kitchencounter",
    "plate" : "kitchencounter",
    "plate_1" : "kitchencounter",
    "breadslice" : "kitchencounter",
    "apple": "cabinet",
    "salmon" : "kitchencounter",
    "water": "faucet", 
    "pan" : "cabinet", 
    "glass_1" : "cabinet",
    "glass" : "cabinet", 
    "coffee": "cabinet",
    "waterglass": "kitchencounter",
    "waterglass_1": "kitchencounter",
    "eggs": "cabinet",
    "banana": "cabinet",
    "knife": "cabinet",
    "pizza-base": "cabinet",
    "soap": "cabinet",
    "washingsponge": "cabinet"
}

# scene_description = "robot is at cabinet; human is at kitchencounter, mop is in cabinet; \
#                      plate, plate_1, dishbowl, dishbowl_1, mug, cereal, milk, breadslice, salmon, waterglass, waterglass_1 are at kitchencounter; \
#                      water at faucet; soap, washingsponge, knife, eggs, apple, banana, pizza-base, pan, glass, glass_1, coffee are in cabinet"

tasks_list = [
    "prepare food",
    "prepare breakfast cereal",
    "prepare breakfast toast",
    "prepare lunch salmon",
    "serve the food cereal",
    "serve a drink water",
    "serve a drink coffee",
    "serve dinner pizza",
    "serve breakfast eggs",
    "serve breakfast fruits",
    "wash the dishes" ]

location_description = [
    "kitchencounter",
    "cabinet: can be opened and closed",
    "stove: can be opened and closed, and switched on and off, for cooking",
    "fridge: can be opened and closed, and switched on and off",
    "microwave: can be opened and closed, and switched on and off, for baking",
    "coffeemaker: can be opened and closed, and switched on and off",
    "coffeetable",
    "faucet: can switched on and off, for water"
    "sink: can be opened and closed",
    "oven: can be opened and closed, and switched on and off, for baking",
    "toaster: can be opened and closed and switched on and off, location for toasting"]

# Common movement cost for entire domain for robot
location_cost = [
    ("sink", "sink", 0),
    ("sink", "cabinet", 19),
    ("sink", "faucet", 12),
    ("sink", "stove", 17),
    ("sink", "microwave", 12),
    ("sink", "kitchencounter", 19),  
    ("cabinet", "sink", 13),
    ("cabinet", "cabinet", 0),
    ("cabinet", "faucet", 13),
    ("cabinet", "coffeetable", 11),
    ("cabinet", "kitchencounter", 13),
    ("cabinet", "fridge", 13),
    ("cabinet", "oven", 10),
    ("cabinet", "microwave", 18),
    ("cabinet", "stove", 14),
    ("cabinet", "coffeemaker", 20),
    ("cabinet", "toaster", 10),
    ("faucet", "sink", 16),
    ("faucet", "cabinet", 14),
    ("faucet", "faucet", 0),
    ("faucet", "coffeetable", 12),
    ("faucet", "kitchencounter", 14),
    ("faucet", "coffeemaker", 11),
    ("faucet", "stove", 19),
    ("coffeetable", "coffeetable", 0),
    ("coffeetable", "kitchencounter", 19),
    ("coffeetable", "cabinet", 15),
    ("coffeetable", "fridge", 17),
    ("coffeetable", "oven", 10),
    ("coffeetable", "microwave", 11),
    ("coffeetable", "faucet", 17),
    ("coffeetable", "coffeemaker", 13),
    ("coffeetable", "stove", 10),
    ("kitchencounter", "coffeetable", 16),
    ("kitchencounter", "kitchencounter", 0),
    ("kitchencounter", "cabinet", 14),
    ("kitchencounter", "fridge", 12),
    ("kitchencounter", "sink", 14),
    ("kitchencounter", "stove", 18),
    ("kitchencounter", "microwave", 17),
    ("kitchencounter", "faucet", 12),
    ("kitchencounter", "toaster", 11),
    ("fridge", "coffeetable", 12),
    ("fridge", "kitchencounter", 13),
    ("fridge", "cabinet", 18),
    ("fridge", "fridge", 0),
    ("fridge", "stove", 15),
    ("fridge", "microwave", 19),
    ("fridge", "toaster", 20),
    ("oven", "cabinet", 15),
    ("oven", "oven", 0),
    ("oven", "coffeetable", 15),
    ("oven", "microwave", 17),
    ("microwave", "cabinet", 17),
    ("microwave", "oven", 16),
    ("microwave", "coffeetable", 16),
    ("microwave", "microwave", 0),
    ("microwave", "sink", 17),
    ("microwave", "stove", 15),
    ("microwave", "kitchencounter", 13),
    ("microwave", "fridge", 13),
    ("stove", "sink", 12),
    ("stove", "stove", 0),
    ("stove", "microwave", 18),
    ("stove", "kitchencounter", 11),
    ("stove", "cabinet", 16),
    ("stove", "coffeemaker", 14),
    ("stove", "coffeetable", 13),
    ("stove", "faucet", 13),
    ("stove", "fridge", 19),
    ("stove", "toaster", 19),
    ("coffeemaker", "cabinet", 17),
    ("coffeemaker", "coffeemaker", 0),
    ("coffeemaker", "coffeetable", 13),
    ("coffeemaker", "stove", 11),
    ("coffeemaker", "faucet", 14),
    ("toaster", "kitchencounter", 14),
    ("toaster", "stove", 20),
    ("toaster", "toaster", 0),
    ("toaster", "fridge", 15),
    ("toaster", "cabinet", 12)
]

item_description = [
    "dishbowl, dishbowl_1: fragile item, container",
    "milk: food item",
    "cereal: food item",
    "mop : cleaning item",
    "mug: container item"
    "plate, plate_1: fragile item, container",
    "breadslice: food item",
    "apple: food item",
    "salmon: food item",
    "water: food item", 
    "pan: container item", 
    "glass_1, glass: container item", 
    "coffee: food item",
    "waterglass: food item",
    "waterglass_1: food item",
    "eggs: food item",
    "banana: food item",
    "knife: utensil",
    "pizza-base: food item",
    "soap",
    "washingsponge"
]

action_description = \
" In the domain, the robot can perform the following actions: " \
" move(robot, <location>, <location>): The robot moves from the former location to latter location." \
" pick(robot, <item>, <location>) : The robot at the location picks up a item which is at the same location and is not inhand already and is not broken. After pick action the item is in the hand of the robot and not at location."\
" place(robot, <item>, <location>) : The robot at the location, places the item, which is now not inhand and present (kept/placed) at the location now."\
" clean(robot, <location>): The robot cleans a location using a mop which is in its hand, which may have become dirty due to breakage of a fragile item. After this action the location becomes clean, item that was broken remains broken."\
" put_in(robot, <item>, <item>): The robot places an item of food type which is in its(robot's) hand into a item which acts a container which is currently kept(placed) at a location(container is not in robot hand), both robot and container item must be at same location"\
" agent_switch_on(robot, <location>): The robot at a location, switches on a location which acts like a appliance, like stove for cooking, faucet for water etc. "\
" agent_switch_off(robot, <location>): The robot switches off a location which acts like a appliance. " \
" agent_open(robot, <location>): The robot opens a location which acts like a appliance like cabinet." \
" agent_close(robot, <location>): The robot closes a location which acts like a appliance like cabinet." \
" pick_human(human, <item>, <location>): Same effect as pick action of robot, but there is Bernoulli(0.9) chance of item breaking when human is trying to pick up a fragile item, Bernoulli(0.1) chance when trying to pick up a normal item. In case of breakage the location becomes unclean and the item remains at that location."\
" move_human(human, <location>, <location>): The human moves from former location to latter location, Bernoulli(0.2) of chance of human not moving to the target location."\
" place_human(human, <item>, <location>): Same effect as place action of robot, but there is Bernoulli(0.9) chance of item breaking and falling on the location when human is trying to place a fragile item at a location, Bernoulli(0.1) chance of breaking when trying to place up a normal item. In case of breakage the location becomes unclean and item falls to that location and is no longer inhand of the human." \
" clean_human(human, <location>): The human cleans a location using a mop in its hand, which may have become dirty due to breakage of a fragile item at a location"\
" put_in_human(human, <item>, <item>): The human places an item of food type which is in its(human's) hand into a item which acts a container which is currently kept at a location(container is not in human hand), both human and container item must be at same location. There is a Bernoulli(0.9) chance the container breaks while placing into the container if fragile, Bernoulli(0.1) of container breakage if not fragile, breakage happens when item falls into the container."\
" human_switch_on(human, <location>): Similar to agent_switch_on action of robot, instead human switches on a appliance with a probabilty of successfull switch on being Bernoulli(0.9)."\
" human_switch_off(human, <location>): Similar to agent_switch_off action of robot, instead human switches off a appliance with a probabilty of successfull switch off being Bernoulli(0.9)."\
" human_open(human, <location>): Similar to agent_open action of robot, instead human opens a location with a success probability of Bernoulli(0.8)."\
" human_close(human, <location>): Similar to agent_close action of robot, instead human closes a location with a success probability of Bernoulli(0.8) that location is closed"

general_description = f"This is a household domain with two actors, robot and human,\
different item instances as mentioned in the list {item_description} and locations mentioned in {location_description}. \
In this domain, the two actors can jointly look to achieve a high level tasks from a fixed set as listed in {tasks_list}, \
that can be only done using a sequence of low level actions described in {action_description}.\
The robot actions has costs associated with it as described in {location_cost} unlike the human which has no movement costs. \
\"Important\": Consider both the cost of robot movement and that human move actions have no cost but human actions are be probabilistic, meaning the human actions may result in failure cases or deviate from expected outcomes, while generating plans to mitigate these uncertainies.\
Also, ensure that all actions selected as part of plan are consistent with the current environment state like current locations of robot and human, current location of items and the preconditions of actions are satisfied before execution and correct item or location types are chosen for respective actions.\
Your task is to generate action plans (action sequences) for achieving jointly achieving two high level tasks, \
given the action descriptions, task descriptions and initial states (locations) of item instances, robot, human. \
Do not assume out of domain information while generating the action plans."

def get_task_prompts(task_1 = "Prepare Salmon", task_2 = "Serve Water"):
    task_prompts = f"Generate combined plan to complete both the tasks: {task_1} (description: {task_description[task_1]}) and {task_2} (description: {task_description[task_2]}), \
                with the items currently at locations given in the list {scene_description}, given current robot location is cabinet; current human location is kitchencounter."

    return task_prompts

output_format = """
Example Plan(s) for Prepare Food Task:
1. [pick(robot, apple, cabinet); move(robot, cabinet, kitchencounter); put_in(robot, apple, plate); pick(robot, plate, kitchencounter); move(robot, kitchencounter, coffeetable); place(robot, plate, coffeetable);]
2. [move_human(human, kitchencounter, cabinet); pick_human(human, apple, cabinet); move_human(human, cabinet, kitchencounter); put_in_human(human, apple, plate); pick_human(human, plate, kitchencounter); move_human(human, kitchencounter, coffeetable); place_human(human, plate, coffeetable);]

Given the input, first explain your reasoning, and then provide a structured action plan.

The example output format must be as follows:

Explanation:
<Your reasoning and breakdown of the situation here>

Plan:
[pick(robot, apple, cabinet); move(human, kitchencounter, stove); ...]

- The plan must be syntactically correct (e.g., action(args)).
- The plan must contain a maximum of 55 actions.
- Each action should be separated by a semicolon.
- No extra text should be present after the 'Plan:' section.

Now generate the output accordingly.
"""

class ChatSession:
    def __init__(self, save_dir="chat_logs"):
        self.outputs = []
        self.messages = []
        self.client = Groq()
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)

    def ask_initial(self, prompt):
        self.messages = [{"role": "user", "content": prompt}]
        response = self._chat()
        self.outputs.append(response)
        return response

    def ask_reprompt(self, correction_prompt):
        self.messages.append({"role": "assistant", "content": self.outputs[-1]})
        self.messages.append({"role": "user", "content": correction_prompt})
        response = self._chat()
        self.outputs.append(response)
        return response

    def _chat(self):
        completion = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=self.messages,
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=False
        )
        reply = completion.choices[0].message.content.strip()
        self.messages.append({"role": "assistant", "content": reply})
        return reply
    
    def parse_plan_from_output(self, output=None):
        if output is None:
            output = self.outputs[-1] if self.outputs else ""
        match = re.search(r"Plan:\s*(\[[^\]]*\])", output, re.DOTALL)
        if match:
            plan_str = match.group(1)
            return plan_str

    def save_outputs(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.save_dir / f"session_{timestamp}.json"
        log_data = {
            "messages": self.messages,
            "outputs": self.outputs,
            "timestamp": timestamp,
        }
        with open(filename, "w") as f:
            json.dump(log_data, f, indent=2)
        print(f"[Session saved to {filename}]")

# session = ChatSession()
# output = session.ask_initial(general_description + task_prompts + output_format)
# print(output)
# output = session.ask_reprompt("Plan failed due to human breaking dishbowl continue from that action.")
# print(output)