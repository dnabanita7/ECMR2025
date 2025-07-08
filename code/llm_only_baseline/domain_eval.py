import random
import re

class HouseholdDomain:
    def __init__(self):
        self.robot_location = 'cabinet'
        self.human_location = 'kitchencounter'

        self.all_locations = [
            "kitchencounter", "cabinet", "stove", "fridge", "microwave",
            "coffeemaker", "coffeetable", "faucet", "sink", "oven", "toaster"
        ]

        self.all_items = [
            "dishbowl", "dishbowl_1", "milk", "cereal", "mop", "mug",
            "plate", "plate_1", "breadslice", "apple", "salmon", "water",
            "pan", "glass", "glass_1", "coffee", "waterglass", "waterglass_1", "eggs",
            "banana", "knife", "pizza-base", "soap", "washingsponge"
        ]

        self.fragile_items = {
            "dishbowl", "dishbowl_1", "plate", "plate_1", "glass", "glass_1", "waterglass", "waterglass_1"
        }

        self.container_items = {
            "dishbowl", "dishbowl_1", "mug", "plate", "plate_1", "pan", "glass", "glass_1"
        }

        self.items_in_hand = {'robot': [], 'human': []}
        self.broken_items = set()
        self.unclean_locations = set()
        self.item_locations = {
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

        self.appliances_on = set()
        self.open_appliances = set()

        self.actions = {}
        self.register_all_actions()

        self.state_log = []
        self.error_log = []

        self.update_world_state()  # Log initial state here!

    def is_fragile(self, item):
        return item in self.fragile_items

    def is_container(self, item):
        return item in self.container_items

    def bernoulli_result(self, p):
        return random.random() < p

    def register(self, name):
        def decorator(func):
            self.actions[name] = func
            return func
        return decorator

    def update_world_state(self):
        world_state = {
            "robot_location": self.robot_location,
            "human_location": self.human_location,
            "items_in_hand": {
                "robot": list(self.items_in_hand['robot']),
                "human": list(self.items_in_hand['human'])
            },
            "item_locations": self.item_locations,
            "broken_items": list(self.broken_items),
            "unclean_locations": list(self.unclean_locations),
            "appliances_on": list(self.appliances_on),
            "open_appliances": list(self.open_appliances)
        }

        self.state_log.append(world_state)

        if len(self.error_log) > 0:
            return True, self.state_log, self.error_log

        return False, self.state_log, self.error_log

    def register_all_actions(self):
        @self.register("move")
        def move(robot, loc_from, loc_to):
            if robot == "robot" and self.robot_location == loc_from:
                self.robot_location = loc_to
            else:
                print(f"Check action of move {loc_from} {loc_to}.") 

        @self.register("pick")
        def pick(robot, item, location):
            if robot == "robot" and self.robot_location == location and \
               self.item_locations.get(item) == location and item not in self.broken_items:
                if item not in self.items_in_hand['robot']:
                    self.items_in_hand['robot'].append(item)
                    del self.item_locations[item]
            else:
                print(f"Check action of pick {item} {location}.")   

        @self.register("place")
        def place(robot, item, location):
            if robot == "robot" and (item in self.items_in_hand['robot']) and self.robot_location == location:
                self.items_in_hand['robot'].remove(item)
                self.item_locations[item] = location
            else:
                print(f"Check action of place {item} {location}.")   

        @self.register("clean")
        def clean(robot, location):
            if robot == "robot" and self.robot_location == location and ('mop' in self.items_in_hand['robot']):
                self.unclean_locations.discard(location)
            else:
                print(f"Check action of clean {location}.")   

        @self.register("put_in")
        def put_in(robot, item, container):
            if robot == "robot" and (item in self.items_in_hand['robot']) and \
                self.item_locations.get(container) == self.robot_location and self.is_container(container):
                self.items_in_hand['robot'].remove(item)
                self.item_locations[item] = self.robot_location
            else:
                print(f"Check action of put_in {item} {container}.")

        @self.register("agent_switch_on")
        def agent_switch_on(robot, appliance):
            if robot == "robot" and self.robot_location == appliance:
                self.appliances_on.add(appliance)
            else:
                print(f"Check action of agent_switch_on {appliance}.")     

        @self.register("agent_switch_off")
        def agent_switch_off(robot, appliance):
            if robot == "robot" and self.robot_location == appliance:
                self.appliances_on.discard(appliance)
            else:
                print(f"Check action of agent_switch_off {appliance}.")         

        @self.register("agent_open")
        def agent_open(robot, appliance):
            if robot == "robot" and self.robot_location == appliance:
                self.open_appliances.add(appliance)
            else:
                print(f"Check action of agent_open {appliance}.")

        @self.register("agent_close")
        def agent_close(robot, appliance):
            if robot == "robot" and self.robot_location == appliance:
                self.open_appliances.discard(appliance)
            else:
                print(f"Check action of agent_close {appliance}.")

        @self.register("pick_human")
        def pick_human(human, item, location):
            if human == "human" and self.human_location == location and \
               item not in self.items_in_hand['human'] and self.item_locations.get(item) == location:
                break_prob = 0.9 if self.is_fragile(item) else 0.01
                if self.bernoulli_result(1 - break_prob):
                    self.items_in_hand['human'].append(item)
                    self.item_locations.pop(item, None)
                else:
                    self.broken_items.add(item)
                    self.unclean_locations.add(location)
                    self.error_log.append({f"Item broken {item} at {self.human_location} while picking"})
            else:
                print(f"Human cannot pick {item} at {location}.")

        @self.register("move_human")
        def move_human(human, loc_from, loc_to):
            if human == "human" and self.human_location == loc_from:
                if self.bernoulli_result(0.8):
                    self.human_location = loc_to
                else:
                    self.error_log.append({f"Human failed to move to {loc_to}"})
            else:
                print(f"Check action of human_move {loc_from} {loc_to}.")

        @self.register("place_human")
        def place_human(human, item, location):
            if human == "human" and (item in self.items_in_hand['human']) and self.human_location == location:
                break_prob = 0.9 if self.is_fragile(item) else 0.1
                if self.bernoulli_result(1 - break_prob):
                    self.item_locations[item] = location
                else:
                    self.broken_items.add(item)
                    self.unclean_locations.add(location)
                    self.error_log.append({f"Item broken {item} at {self.human_location} while placing"})
                self.items_in_hand['human'].remove(item)
            else:
                print(f"Check action of place_human {item} {location}")

        @self.register("clean_human")
        def clean_human(human, location):
            if human == "human" and self.human_location == location and ('mop' in self.items_in_hand['human']):
                self.unclean_locations.discard(location)
            else:
                print(f"Check action of clean_human {location}")

        @self.register("put_in_human")
        def put_in_human(human, item, container):
            if human == "human" and (item in self.items_in_hand['human']) and \
                self.item_locations.get(container) == self.human_location and self.is_container(container):
                break_prob = 0.9 if self.is_fragile(container) else 0.1
                if self.bernoulli_result(1 - break_prob):
                    self.item_locations[item] = self.human_location
                else:
                    self.broken_items.add(container)
                    self.unclean_locations.add(self.human_location)
                    self.error_log.append({f"Item broken {container} at {self.human_location} while put_in"})
                self.items_in_hand['human'].remove(item)
                self.item_locations[item] = self.human_location
            else:
                print(f"Check action of put_in_human. {item} {container}")

        @self.register("human_switch_on")
        def human_switch_on(human, appliance):
            if human == "human" and self.human_location == appliance:
                if self.bernoulli_result(0.9):
                    self.appliances_on.add(appliance)
                else:
                    self.error_log.append({f"Human failed to switchon {appliance}"})
            else:
                print(f"Check action of human_switch_on {appliance}")

        @self.register("human_switch_off")
        def human_switch_off(human, appliance):
            if human == "human" and self.human_location == appliance :
                if self.bernoulli_result(0.9):
                    self.appliances_on.discard(appliance)
                else:
                    self.error_log.append({f"Human failed to switchoff {appliance}"})
            else:
                print(f"Check action of human_switch_off {appliance}")

        @self.register("human_open")
        def human_open(human, appliance):
            if human == "human" and self.human_location == appliance:
                if self.bernoulli_result(0.8):
                    self.open_appliances.add(appliance)
                else:
                    self.error_log.append({f"Human failed to open {appliance}"})
            else:
                print(f"Check action of human_open {appliance}")

        @self.register("human_close")
        def human_close(human, appliance):
            if human == "human" and self.human_location == appliance :
                if self.bernoulli_result(0.8):
                    self.open_appliances.discard(appliance)
                else:
                    self.error_log.append({f"Human failed to close {appliance}"})
            else:
                print(f"Check action of human_close {appliance}")

    def parse_line(self, line):
        match = re.match(r'(\w+)\(([^)]+)\);?', line.strip())
        if match:
            action = match.group(1)
            args = [arg.strip() for arg in match.group(2).split(',')]
            return action, args
        return None, None
    
    def parse_plan_string(self, plan_string):
        return [line.strip() + ';' for line in plan_string.strip()[1:-1].split(';') if line.strip()]
    
def simulate_plan(plan):
    state = None
    domain = HouseholdDomain()
    plan = domain.parse_plan_string(plan)
    for line in plan:
        action, args = domain.parse_line(line)
        print(action)
        if action in domain.actions:
            domain.actions[action](*args)
        failure, state, error = domain.update_world_state()
        if failure:
            return False, state, error
    return state

# plan = "[move_human(human, kitchencounter, cabinet); pick_human(human, mop, cabinet); put_in_human(human, mop, glass);]"
# print(simulate_plan(plan))