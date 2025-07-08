import sys
import os
import json
import time
import subprocess

sys.path.append('/home/ayush/iiith/RRC/Task_Planning/virtualhome-2.2.0/simulation/')
from unity_simulator.comm_unity import UnityCommunication

OUTPUT_PATH = "/home/ayush/iiith/RRC/Task_Planning/virtualhome-2.2.0/simulation/unity_simulator/Output/script/0"
OUTPUT_PATH_1 = "/home/ayush/iiith/RRC/Task_Planning/virtualhome-2.2.0/simulation/unity_simulator/Output/script/1"

### Utils nodes
def find_nodes(graph, **kwargs):
    if len(kwargs) == 0:
        return None
    else:
        k, v = next(iter(kwargs.items()))
        return [n for n in graph['nodes'] if n[k] == v]
    
def find_edges_from(graph, id):
    nb_list = [(e['relation_type'], e['to_id']) for e in graph['edges'] if e['from_id'] == id]
    return [(rel, find_nodes(graph, id=n_id)[0]) for (rel, n_id) in nb_list]

def clean_graph(graph):
    new_nodes = []
    for n in graph['nodes']:
        nc = dict(n)
        if 'bounding_box' in nc:
            del nc['bounding_box']
        new_nodes.append(nc)
    return {'nodes': new_nodes, 'edges': list(graph['edges'])}

def remove_edges(graph, n, fr=True, to=True):
    n_id = n['id']
    new_edges = [e for e in graph['edges'] if 
                 (e['from_id'] != n_id or not fr) and (e['to_id'] != n_id or not to)]
    graph['edges'] = new_edges

def remove_edge(graph, fr_id, rel, to_id):
    new_edges = [e for e in graph['edges'] if 
                 not (e['from_id'] == fr_id and e['to_id'] == to_id and e['relation_type'] == rel)]
    graph['edges'] = new_edges
    
def add_node(graph, n):
    graph['nodes'].append(n)

def add_edge(graph, fr_id, rel, to_id):
    graph['edges'].append({'from_id': fr_id, 'relation_type': rel, 'to_id': to_id})

def set_domain_graph(comm, domain_name=""):
    # For every domain add intial location, new objects, and init-state for each object
    success, graph = comm.environment_graph()
    spawn_locations = ["kitchen", "bathroom"] # Initial location
    positions = [[0, 0, 0], [1, 1, 0]]

    if domain_name == "instance_clean_the_room_bathroom":
        spawn_locations = ["bathroom", "bathroom"]
        bathtub_node = next((node for node in graph['nodes'] if 'bathtub' in node['class_name']), None)
        bathroomcabinet_node = next((node for node in graph['nodes'] if 'bathroomcabinet' in node['class_name']), None)
        positions[0] = [bathtub_node["obj_transform"]["position"][0] + 0.5, bathtub_node["obj_transform"]["position"][1] + 0.25, 0]
        positions[1] = [bathroomcabinet_node["obj_transform"]["position"][0] + 0.5, bathroomcabinet_node["obj_transform"]["position"][1] + 0.5, 0]
        bathroom_counter = next((node for node in graph['nodes'] if 'bathroomcounter' in node['class_name']), None)

        add_node(graph, {'class_name': 'broom',
                        'category': 'Props', 
                        'id': 1000}
                        )
        
        add_node(graph, {'class_name': 'trash',
                        'category': 'Props', 
                        'id': 1001,
                        'properties': ['GRABBABLE', 'MOVABLE'],
                        'states': [],
                        'prefab_name': 'Garbage_can_8'}
                        )

        floor_node = find_nodes(graph, class_name='floor')[0]
        if floor_node:
            add_edge(graph, 1000, 'ON', floor_node["id"])
            add_edge(graph, 1001, 'ON', floor_node["id"])

        for obj_name in ["towel", "washingsponge", "soap", "trash_can"]: # 
            obj = find_nodes(graph, class_name=obj_name)
            if obj:
                obj = obj[0]
                obj["obj_transform"]["position"] = bathroom_counter["obj_transform"]["position"] + [0.1, 0.1, 0.1]
                add_edge(graph, obj["id"], "ON", bathroom_counter["id"])
                print(obj_name, ":", obj["id"])
        
        print("cabinet:", bathroomcabinet_node["id"], "tub:", bathtub_node["id"], "counter:", bathroom_counter["id"])

    elif domain_name == "instance_clean_the_room_kitchen":
        spawn_locations = ["kitchen", "kitchen"]
        kitchen_node = find_nodes(graph, class_name='kitchen')[0]
        cabinet = next((node for node in graph['nodes'] if 'kitchencabinet' in node['class_name']), None)
        counter = next((node for node in graph['nodes'] if 'kitchencounter' in node['class_name']), None)
        positions[0] = [cabinet["obj_transform"]["position"][0] + 0.5, cabinet["obj_transform"]["position"][1] + 0.25, 0]
        positions[1] = [counter["obj_transform"]["position"][0] + 0.5, counter["obj_transform"]["position"][1] + 0.5, 0]

        add_node(graph, {'class_name': 'broom',
                'category': 'Props', 
                'id': 1000, 
                'properties': ['GRABBABLE', 'MOVABLE'], 
                'states': [],}
                )
        floor_node = find_nodes(graph, class_name='floor')[-1]
        add_edge(graph, 1000, 'ON', 208)

        # floor_nodes = [node for node in find_nodes(graph, class_name='floor')
        #        if any(edge['from_id'] == node['id'] and edge['to_id'] == kitchen_node['id'] 
        #               and edge['relation_type'] == "INSIDE" for edge in graph['edges'])]
        # if floor_nodes:
        #     selected_floor = floor_nodes[0]
        #     print(f"Using Floor ID: {selected_floor['id']}")
        #     add_edge(graph, 1000, 'ON', selected_floor["id"])

        for obj_name in ["towel", "washingsponge", "soap"]:
            obj = find_nodes(graph, class_name=obj_name)
            if obj:
                obj = obj[0]
                obj["obj_transform"]["position"] = counter["obj_transform"]["position"] + [0.1, 0.1, 0.1]
                remove_edges(graph, obj)
                add_edge(graph, obj["id"], "ON", counter["id"])
                print(obj_name, ":", obj["id"])
        
        print("cabinet:", cabinet["id"], "kitchen:", kitchen_node["id"], "counter:", counter["id"])

    elif domain_name == "instance_do_the_laundry":
        spawn_locations = ["bathroom", "bathroom"]
        bathtub_node = next((node for node in graph['nodes'] if 'bathtub' in node['class_name']), None)
        bathroomcabinet_node = next((node for node in graph['nodes'] if 'bathroomcabinet' in node['class_name']), None)
        positions[0] = [bathtub_node["obj_transform"]["position"][0] + 0.5, bathtub_node["obj_transform"]["position"][1] + 0.25, 0]
        positions[1] = [bathroomcabinet_node["obj_transform"]["position"][0] + 0.5, bathroomcabinet_node["obj_transform"]["position"][1] + 0.5, 0]
        bathroom_counter = next((node for node in graph['nodes'] if 'bathroomcounter' in node['class_name']), None)
        washing = next((node for node in graph['nodes'] if 'washingmachine' in node['class_name']), None)

        add_node(graph, {'class_name': 'broom',
                        'category': 'Props', 
                        'id': 1000}
                        )
        floor_node = find_nodes(graph, class_name='floor')[0]

        if floor_node:
            add_edge(graph, 1000, 'ON', floor_node["id"])

        for obj_name in ["shirt", "dishwashingliquid"]:
            obj = find_nodes(graph, class_name=obj_name)
            if obj:
                obj = obj[0]
                obj["obj_transform"]["position"] = bathroom_counter["obj_transform"]["position"] + [0.1, 0.1, 0.1]
                add_edge(graph, obj["id"], "ON", bathroom_counter["id"])
                print(obj_name, ":", obj["id"])
            
        print("cabinet:", bathroomcabinet_node["id"], "washing:", washing["id"], "counter:", bathroom_counter["id"])

    elif domain_name == "instance_prepare_breakfast_cereal":
        spawn_locations = ["kitchen", "kitchen"]
        kitchen_node = find_nodes(graph, class_name='kitchen')[0]
        cabinet = next((node for node in graph['nodes'] if 'kitchencabinet' in node['class_name']), None)
        counter = next((node for node in graph['nodes'] if 'kitchencounter' in node['class_name']), None)
        fridge = next((node for node in graph['nodes'] if 'fridge' in node['class_name']), None)
        positions[0] = [cabinet["obj_transform"]["position"][0] + 0.5, cabinet["obj_transform"]["position"][1] + 0.25, 0]
        positions[1] = [fridge["obj_transform"]["position"][0] + 0.5, fridge["obj_transform"]["position"][1] + 0.5, 0]

        add_node(graph, {'class_name': 'broom',
                'category': 'Props', 
                'id': 1000, 
                'properties': ['GRABBABLE', 'MOVABLE'], 
                'states': [],}
                )
        floor_node = find_nodes(graph, class_name='floor')[-1]
        add_edge(graph, 1000, 'ON', 208)

        # floor_nodes = [node for node in find_nodes(graph, class_name='floor')
        #        if any(edge['from_id'] == node['id'] and edge['to_id'] == kitchen_node['id'] 
        #               and edge['relation_type'] == "INSIDE" for edge in graph['edges'])]
        # if floor_nodes:
        #     selected_floor = floor_nodes[0]
        #     print(f"Using Floor ID: {selected_floor['id']}")
        #     add_edge(graph, 1000, 'ON', selected_floor["id"])

        for obj_name in ["mug", "dishbowl", "milk", "cereal"]:
            obj = find_nodes(graph, class_name=obj_name)
            if obj:
                obj = obj[0]
                obj["obj_transform"]["position"] = counter["obj_transform"]["position"] + [0.1, 0.1, 0.1]
                remove_edges(graph, obj)
                add_edge(graph, obj["id"], "ON", counter["id"])
                print(obj_name, ":", obj["id"])
        
        print("cabinet:", cabinet["id"], "kitchen:", kitchen_node["id"], "counter:", counter["id"], "fridge:", fridge["id"])

    elif domain_name == "instance_prepare_breakfast_toast":
        spawn_locations = ["kitchen", "kitchen"]

        kitchen_node = find_nodes(graph, class_name='kitchen')[0]
        cabinet = next((node for node in graph['nodes'] if 'kitchencabinet' in node['class_name']), None)
        counter = next((node for node in graph['nodes'] if 'kitchencounter' in node['class_name']), None)
        toaster = next((node for node in graph['nodes'] if 'toaster' in node['class_name']), None)
        stove = next((node for node in graph['nodes'] if 'stove' in node['class_name']), None)
        fridge = next((node for node in graph['nodes'] if 'fridge' in node['class_name']), None)

        positions[0] = [cabinet["obj_transform"]["position"][0] + 0.5, cabinet["obj_transform"]["position"][1] + 0.25, 0]
        positions[1] = [fridge["obj_transform"]["position"][0] + 0.5, fridge["obj_transform"]["position"][1] + 0.5, 0]

        add_node(graph, {'class_name': 'broom',
                'category': 'Props', 
                'id': 1000, 
                'properties': ['GRABBABLE', 'MOVABLE'], 
                'states': [],}
                )
        floor_node = find_nodes(graph, class_name='floor')[-1]
        add_edge(graph, 1000, 'ON', 208)

        # floor_nodes = [node for node in find_nodes(graph, class_name='floor')
        #        if any(edge['from_id'] == node['id'] and edge['to_id'] == kitchen_node['id'] 
        #               and edge['relation_type'] == "INSIDE" for edge in graph['edges'])]
        # if floor_nodes:
        #     selected_floor = floor_nodes[0]
        #     print(f"Using Floor ID: {selected_floor['id']}")
        #     add_edge(graph, 1000, 'ON', selected_floor["id"])

        for obj_name in ["plate", "breadslice"]:
            objects = find_nodes(graph, class_name=obj_name)
            if objects:
                for obj in objects:  # Iterate over all found objects
                    obj["obj_transform"]["position"] = [
                        counter["obj_transform"]["position"][0] + 0.1,
                        counter["obj_transform"]["position"][1] + 0.1,
                        counter["obj_transform"]["position"][2] + 0.1
                    ]
                    remove_edges(graph, obj)
                    add_edge(graph, obj["id"], "ON", counter["id"])
                    print(obj_name, ":", obj["id"])
  
        print("cabinet:", cabinet["id"], "kitchen:", kitchen_node["id"], "counter:", counter["id"], 
              "toaster:", toaster["id"], "fridge:", fridge["id"], "stove:", stove["id"])

    elif domain_name == "instance_prepare_food":
        spawn_locations = ["kitchen", "kitchen"]
        kitchen_node = find_nodes(graph, class_name='kitchen')[0]
        cabinet = next((node for node in graph['nodes'] if 'kitchencabinet' in node['class_name']), None)
        counter = next((node for node in graph['nodes'] if 'kitchencounter' in node['class_name']), None)

        positions[0] = [cabinet["obj_transform"]["position"][0] + 0.5, cabinet["obj_transform"]["position"][1] + 0.25, 0]
        positions[1] = [counter["obj_transform"]["position"][0] + 0.5, counter["obj_transform"]["position"][1] + 0.5, 0]

        add_node(graph, {'class_name': 'broom',
                'category': 'Props', 
                'id': 1000, 
                'properties': ['GRABBABLE', 'MOVABLE'], 
                'states': [],}
                )
        floor_node = find_nodes(graph, class_name='floor')[-1]
        add_edge(graph, 1000, 'ON', 208)

        # floor_nodes = [node for node in find_nodes(graph, class_name='floor')
        #        if any(edge['from_id'] == node['id'] and edge['to_id'] == kitchen_node['id'] 
        #               and edge['relation_type'] == "INSIDE" for edge in graph['edges'])]
        # if floor_nodes:
        #     selected_floor = floor_nodes[0]
        #     print(f"Using Floor ID: {selected_floor['id']}")
        #     add_edge(graph, 1000, 'ON', selected_floor["id"])

        for obj_name in ["plate", "apple", "dishbowl"]:
            objects = find_nodes(graph, class_name=obj_name)
            if objects:
                for obj in objects:  # Iterate over all found objects
                    obj["obj_transform"]["position"] = [
                        counter["obj_transform"]["position"][0] + 0.1,
                        counter["obj_transform"]["position"][1] + 0.1,
                        counter["obj_transform"]["position"][2] + 0.1
                    ]
                    remove_edges(graph, obj)
                    add_edge(graph, obj["id"], "ON", counter["id"])
                    print(obj_name, ":", obj["id"])
  
        print("cabinet:", cabinet["id"], "kitchen:", kitchen_node["id"], "counter:", counter["id"])
    
    elif domain_name == "instance_prepare_lunch_salmon":
        spawn_locations = ["kitchen", "kitchen"]

        kitchen_node = find_nodes(graph, class_name='kitchen')[0]
        cabinet = next((node for node in graph['nodes'] if 'kitchencabinet' in node['class_name']), None)
        counter = next((node for node in graph['nodes'] if 'kitchencounter' in node['class_name']), None)
        toaster = next((node for node in graph['nodes'] if 'toaster' in node['class_name']), None)
        stove = next((node for node in graph['nodes'] if 'stove' in node['class_name']), None)
        microwave = next((node for node in graph['nodes'] if 'microwave' in node['class_name']), None)
        fridge = next((node for node in graph['nodes'] if 'fridge' in node['class_name']), None)

        positions[0] = [cabinet["obj_transform"]["position"][0] + 0.5, cabinet["obj_transform"]["position"][1] + 0.25, 0]
        positions[1] = [fridge["obj_transform"]["position"][0] + 0.5, fridge["obj_transform"]["position"][1] + 0.5, 0]

        add_node(graph, {'class_name': 'broom',
                'category': 'Props', 
                'id': 1000, 
                'properties': ['GRABBABLE', 'MOVABLE'], 
                'states': [],}
                )
        floor_node = find_nodes(graph, class_name='floor')[-1]
        add_edge(graph, 1000, 'ON', 208)

        # floor_nodes = [node for node in find_nodes(graph, class_name='floor')
        #        if any(edge['from_id'] == node['id'] and edge['to_id'] == kitchen_node['id'] 
        #               and edge['relation_type'] == "INSIDE" for edge in graph['edges'])]
        # if floor_nodes:
        #     selected_floor = floor_nodes[0]
        #     print(f"Using Floor ID: {selected_floor['id']}")
        #     add_edge(graph, 1000, 'ON', selected_floor["id"])

        for obj_name in ["plate", "salmon"]:
            objects = find_nodes(graph, class_name=obj_name)
            if objects:
                for obj in objects:  # Iterate over all found objects
                    obj["obj_transform"]["position"] = [
                        counter["obj_transform"]["position"][0] + 0.1,
                        counter["obj_transform"]["position"][1] + 0.1,
                        counter["obj_transform"]["position"][2] + 0.1
                    ]
                    remove_edges(graph, obj)
                    add_edge(graph, obj["id"], "ON", counter["id"])
                    print(obj_name, ":", obj["id"])
  
        print("cabinet:", cabinet["id"], "kitchen:", kitchen_node["id"], "counter:", counter["id"], 
              "toaster:", toaster["id"], "fridge:", fridge["id"], "stove:", stove["id"], "microwave", microwave["id"])

    elif domain_name == "instance_serve_a_drink_coffee":
        spawn_locations = ["livingroom", "livingroom"]

        kitchen_node = find_nodes(graph, class_name='kitchen')[0]
        counter = next((node for node in graph['nodes'] if 'kitchencounter' in node['class_name']), None)
        cabinet = next((node for node in graph['nodes'] if 'kitchencabinet' in node['class_name']), None)
        table = next((node for node in graph['nodes'] if 'coffeetable' in node['class_name']), None)
        coffeemaker = next((node for node in graph['nodes'] if 'coffeemaker' in node['class_name']), None)
        stove = next((node for node in graph['nodes'] if 'stove' in node['class_name']), None)
        faucet = next((node for node in graph['nodes'] if 'faucet' in node['class_name']), None)

        positions[0] = [cabinet["obj_transform"]["position"][0] + 0.5, cabinet["obj_transform"]["position"][1] + 0.25, 0]
        positions[1] = [table["obj_transform"]["position"][0] + 0.5, table["obj_transform"]["position"][1] + 0.5, 0]

        add_node(graph, {'class_name': 'broom',
                'category': 'Props', 
                'id': 1000, 
                'properties': ['GRABBABLE', 'MOVABLE'], 
                'states': [],}
                )
        floor_node = find_nodes(graph, class_name='floor')[-1]
        add_edge(graph, 1000, 'ON', 208)

        # floor_nodes = [node for node in find_nodes(graph, class_name='floor')
        #        if any(edge['from_id'] == node['id'] and edge['to_id'] == kitchen_node['id'] 
        #               and edge['relation_type'] == "INSIDE" for edge in graph['edges'])]
        # if floor_nodes:
        #     selected_floor = floor_nodes[0]
        #     print(f"Using Floor ID: {selected_floor['id']}")
        #     add_edge(graph, 1000, 'ON', selected_floor["id"])

        for obj_name in ["mug", "waterglass", "pan", "coffee"]:
            objects = find_nodes(graph, class_name=obj_name)
            if objects:
                for obj in objects:  # Iterate over all found objects
                    obj["obj_transform"]["position"] = [
                        counter["obj_transform"]["position"][0] + 0.1,
                        counter["obj_transform"]["position"][1] + 0.1,
                        counter["obj_transform"]["position"][2] + 0.1
                    ]
                    remove_edges(graph, obj)
                    add_edge(graph, obj["id"], "ON", counter["id"])
                    print(obj_name, ":", obj["id"])
  
        print("cabinet:", cabinet["id"], "kitchen:", kitchen_node["id"], "table:", table["id"], 
              "coffeemaker:", coffeemaker["id"], "faucet:", faucet["id"], "stove:", stove["id"])

    elif domain_name == "instance_serve_a_drink_water":
        spawn_locations = ["kitchen", "livingroom"]

        kitchen_node = find_nodes(graph, class_name='kitchen')[0]

        cabinet = next((node for node in graph['nodes'] if 'kitchencabinet' in node['class_name']), None)
        table = next((node for node in graph['nodes'] if 'coffeetable' in node['class_name']), None)
        counter = next((node for node in graph['nodes'] if 'kitchencounter' in node['class_name']), None)
        faucet = next((node for node in graph['nodes'] if 'faucet' in node['class_name']), None)

        positions[0] = [cabinet["obj_transform"]["position"][0] + 0.5, cabinet["obj_transform"]["position"][1] + 0.25, 0]
        positions[1] = [table["obj_transform"]["position"][0] + 0.5, table["obj_transform"]["position"][1] + 0.5, 0]

        add_node(graph, {'class_name': 'broom',
                'category': 'Props', 
                'id': 1000, 
                'properties': ['GRABBABLE', 'MOVABLE'], 
                'states': [],}
                )
        floor_node = find_nodes(graph, class_name='floor')[-1]
        add_edge(graph, 1000, 'ON', 208)

        # floor_nodes = [node for node in find_nodes(graph, class_name='floor')
        #        if any(edge['from_id'] == node['id'] and edge['to_id'] == kitchen_node['id'] 
        #               and edge['relation_type'] == "INSIDE" for edge in graph['edges'])]
        # if floor_nodes:
        #     selected_floor = floor_nodes[0]
        #     print(f"Using Floor ID: {selected_floor['id']}")
        #     add_edge(graph, 1000, 'ON', selected_floor["id"])

        for obj_name in ["mug", "waterglass"]:
            objects = find_nodes(graph, class_name=obj_name)
            if objects:
                for obj in objects:  # Iterate over all found objects
                    obj["obj_transform"]["position"] = [
                        counter["obj_transform"]["position"][0] + 0.1,
                        counter["obj_transform"]["position"][1] + 0.1,
                        counter["obj_transform"]["position"][2] + 0.1
                    ]
                    remove_edges(graph, obj)
                    add_edge(graph, obj["id"], "ON", counter["id"])
                    print(obj_name, ":", obj["id"])
  
        print("cabinet:", cabinet["id"], "kitchen:", kitchen_node["id"], "table:", table["id"], 
              "faucet:", faucet["id"], "counter:", counter["id"])

    elif domain_name == "instance_serve_breakfast_eggs":
        spawn_locations = ["kitchen", "kitchen"]
        kitchen_node = find_nodes(graph, class_name='kitchen')[0]

        cabinet = next((node for node in graph['nodes'] if 'kitchencabinet' in node['class_name']), None)
        counter = next((node for node in graph['nodes'] if 'kitchencounter' in node['class_name']), None)
        stove = next((node for node in graph['nodes'] if 'stove' in node['class_name']), None)
        microwave = next((node for node in graph['nodes'] if 'microwave' in node['class_name']), None)
        sink = next((node for node in graph['nodes'] if 'sink' in node['class_name']), None)

        positions[0] = [cabinet["obj_transform"]["position"][0] + 0.5, cabinet["obj_transform"]["position"][1] + 0.25, 0]
        positions[1] = [counter["obj_transform"]["position"][0] + 0.5, counter["obj_transform"]["position"][1] + 0.5, 0]

        add_node(graph, {'class_name': 'broom',
                'category': 'Props', 
                'id': 1000, 
                'properties': ['GRABBABLE', 'MOVABLE'], 
                'states': [],}
                )
        floor_node = find_nodes(graph, class_name='floor')[-1]
        add_edge(graph, 1000, 'ON', 208)

        # floor_nodes = [node for node in find_nodes(graph, class_name='floor')
        #        if any(edge['from_id'] == node['id'] and edge['to_id'] == kitchen_node['id'] 
        #               and edge['relation_type'] == "INSIDE" for edge in graph['edges'])]
        # if floor_nodes:
        #     selected_floor = floor_nodes[0]
        #     print(f"Using Floor ID: {selected_floor['id']}")
        #     add_edge(graph, 1000, 'ON', selected_floor["id"])

        for obj_name in ["plate", "waterglass", "eggs", "pan"]:
            objects = find_nodes(graph, class_name=obj_name)
            if objects:
                for obj in objects:  # Iterate over all found objects
                    obj["obj_transform"]["position"] = [
                        counter["obj_transform"]["position"][0] + 0.1,
                        counter["obj_transform"]["position"][1] + 0.1,
                        counter["obj_transform"]["position"][2] + 0.1
                    ]
                    remove_edges(graph, obj)
                    add_edge(graph, obj["id"], "ON", counter["id"])
                    print(obj_name, ":", obj["id"])
  
        print("cabinet:", cabinet["id"], "kitchen:", kitchen_node["id"],
              "sink:", sink["id"], "stove:", stove["id"], "counter:", counter["id"], "microwave:", microwave["id"])

    elif domain_name == "instance_serve_breakfast_fruits":
        spawn_locations = ["kitchen", "kitchen"]

        kitchen_node = find_nodes(graph, class_name='kitchen')[0]

        cabinet = next((node for node in graph['nodes'] if 'kitchencabinet' in node['class_name']), None)
        table = next((node for node in graph['nodes'] if 'coffeetable' in node['class_name']), None)
        counter = next((node for node in graph['nodes'] if 'kitchencounter' in node['class_name']), None)

        positions[0] = [cabinet["obj_transform"]["position"][0] + 0.5, cabinet["obj_transform"]["position"][1] + 0.25, 0]
        positions[1] = [table["obj_transform"]["position"][0] + 0.5, table["obj_transform"]["position"][1] + 0.5, 0]

        add_node(graph, {'class_name': 'broom',
                'category': 'Props', 
                'id': 1000, 
                'properties': ['GRABBABLE', 'MOVABLE'], 
                'states': [],}
                )
        floor_node = find_nodes(graph, class_name='floor')[-1]
        add_edge(graph, 1000, 'ON', 208)

        # floor_nodes = [node for node in find_nodes(graph, class_name='floor')
        #        if any(edge['from_id'] == node['id'] and edge['to_id'] == kitchen_node['id'] 
        #               and edge['relation_type'] == "INSIDE" for edge in graph['edges'])]
        # if floor_nodes:
        #     selected_floor = floor_nodes[0]
        #     print(f"Using Floor ID: {selected_floor['id']}")
        #     add_edge(graph, 1000, 'ON', selected_floor["id"])

        for obj_name in ["plate", "dishbowl", "knife", "banana", "apple"]:
            objects = find_nodes(graph, class_name=obj_name)
            if objects:
                for obj in objects:  # Iterate over all found objects
                    obj["obj_transform"]["position"] = [
                        counter["obj_transform"]["position"][0] + 0.1,
                        counter["obj_transform"]["position"][1] + 0.1,
                        counter["obj_transform"]["position"][2] + 0.1
                    ]
                    remove_edges(graph, obj)
                    add_edge(graph, obj["id"], "ON", counter["id"])
                    print(obj_name, ":", obj["id"])
  
        print("cabinet:", cabinet["id"], "kitchen:", kitchen_node["id"], "table:", table["id"], 
              "counter:", counter["id"])

    elif domain_name == "instance_serve_dinner_pizza":
        spawn_locations = ["kitchen", "kitchen"]
        kitchen_node = find_nodes(graph, class_name='kitchen')[0]

        cabinet = next((node for node in graph['nodes'] if 'kitchencabinet' in node['class_name']), None)
        counter = next((node for node in graph['nodes'] if 'kitchencounter' in node['class_name']), None)
        stove = next((node for node in graph['nodes'] if 'stove' in node['class_name']), None)
        microwave = next((node for node in graph['nodes'] if 'microwave' in node['class_name']), None)
        table = next((node for node in graph['nodes'] if 'coffeetable' in node['class_name']), None)

        positions[0] = [cabinet["obj_transform"]["position"][0] + 0.5, cabinet["obj_transform"]["position"][1] + 0.25, 0]
        positions[1] = [counter["obj_transform"]["position"][0] + 0.5, counter["obj_transform"]["position"][1] + 0.5, 0]

        add_node(graph, {'class_name': 'broom',
                'category': 'Props', 
                'id': 1000, 
                'properties': ['GRABBABLE', 'MOVABLE'], 
                'states': [],}
                )
        floor_node = find_nodes(graph, class_name='floor')[-1]
        add_edge(graph, 1000, 'ON', 208)

        # floor_nodes = [node for node in find_nodes(graph, class_name='floor')
        #        if any(edge['from_id'] == node['id'] and edge['to_id'] == kitchen_node['id'] 
        #               and edge['relation_type'] == "INSIDE" for edge in graph['edges'])]
        # if floor_nodes:
        #     selected_floor = floor_nodes[0]
        #     print(f"Using Floor ID: {selected_floor['id']}")
        #     add_edge(graph, 1000, 'ON', selected_floor["id"])

        for obj_name in ["plate", "pizza"]:
            objects = find_nodes(graph, class_name=obj_name)
            if objects:
                for obj in objects:  # Iterate over all found objects
                    obj["obj_transform"]["position"] = [
                        counter["obj_transform"]["position"][0] + 0.1,
                        counter["obj_transform"]["position"][1] + 0.1,
                        counter["obj_transform"]["position"][2] + 0.1
                    ]
                    remove_edges(graph, obj)
                    add_edge(graph, obj["id"], "ON", counter["id"])
                    print(obj_name, ":", obj["id"])
  
        print("cabinet:", cabinet["id"], "kitchen:", kitchen_node["id"], "table:", table["id"], 
              "stove:", stove["id"], "counter:", counter["id"], "microwave:", microwave["id"])

    elif domain_name == "instance_serve_the_food_cereal":
        spawn_locations = ["kitchen", "kitchen"]
        kitchen_node = find_nodes(graph, class_name='kitchen')[0]
        cabinet = next((node for node in graph['nodes'] if 'kitchencabinet' in node['class_name']), None)
        counter = next((node for node in graph['nodes'] if 'kitchencounter' in node['class_name']), None)
        fridge = next((node for node in graph['nodes'] if 'fridge' in node['class_name']), None)
        table = next((node for node in graph['nodes'] if 'coffeetable' in node['class_name']), None)

        positions[0] = [cabinet["obj_transform"]["position"][0] + 0.5, cabinet["obj_transform"]["position"][1] + 0.25, 0]
        positions[1] = [fridge["obj_transform"]["position"][0] + 0.5, fridge["obj_transform"]["position"][1] + 0.5, 0]

        add_node(graph, {'class_name': 'broom',
                'category': 'Props', 
                'id': 1000, 
                'properties': ['GRABBABLE', 'MOVABLE'], 
                'states': [],}
                )
        floor_node = find_nodes(graph, class_name='floor')[-1]
        add_edge(graph, 1000, 'ON', 208)

        # floor_nodes = [node for node in find_nodes(graph, class_name='floor')
        #        if any(edge['from_id'] == node['id'] and edge['to_id'] == kitchen_node['id'] 
        #               and edge['relation_type'] == "INSIDE" for edge in graph['edges'])]
        # if floor_nodes:
        #     selected_floor = floor_nodes[0]
        #     print(f"Using Floor ID: {selected_floor['id']}")
        #     add_edge(graph, 1000, 'ON', selected_floor["id"])

        for obj_name in ["mug", "dishbowl", "milk", "cereal"]:
            obj = find_nodes(graph, class_name=obj_name)
            if obj:
                obj = obj[0]
                obj["obj_transform"]["position"] = counter["obj_transform"]["position"] + [0.1, 0.1, 0.1]
                remove_edges(graph, obj)
                add_edge(graph, obj["id"], "ON", counter["id"])
                print(obj_name, ":", obj["id"])
        
        print("cabinet:", cabinet["id"], "kitchen:", kitchen_node["id"], "counter:", counter["id"], 
              "fridge:", fridge["id"], "table:", table["id"])

    elif domain_name == "instance_wash_the_dishes":
        spawn_locations = ["kitchen", "kitchen"]

        kitchen_node = find_nodes(graph, class_name='kitchen')[0]

        cabinet = next((node for node in graph['nodes'] if 'kitchencabinet' in node['class_name']), None)
        counter = next((node for node in graph['nodes'] if 'kitchencounter' in node['class_name']), None)
        faucet = next((node for node in graph['nodes'] if 'faucet' in node['class_name']), None)
        sink = next((node for node in graph['nodes'] if 'sink' in node['class_name']), None)

        add_node(graph, {'class_name': 'broom',
                'category': 'Props', 
                'id': 1000, 
                'properties': ['GRABBABLE', 'MOVABLE'], 
                'states': [],}
                )
        floor_node = find_nodes(graph, class_name='floor')[-1]
        add_edge(graph, 1000, 'ON', 208)

        # floor_nodes = [node for node in find_nodes(graph, class_name='floor')
        #        if any(edge['from_id'] == node['id'] and edge['to_id'] == kitchen_node['id'] 
        #               and edge['relation_type'] == "INSIDE" for edge in graph['edges'])]
        # if floor_nodes:
        #     selected_floor = floor_nodes[0]
        #     print(f"Using Floor ID: {selected_floor['id']}")
        #     add_edge(graph, 1000, 'ON', selected_floor["id"])

        for obj_name in ["plate", "cleaning_solution", "soap", "washingsponge"]:
            objects = find_nodes(graph, class_name=obj_name)
            if objects:
                for obj in objects:  # Iterate over all found objects
                    obj["obj_transform"]["position"] = [
                        counter["obj_transform"]["position"][0] + 0.1,
                        counter["obj_transform"]["position"][1] + 0.1,
                        counter["obj_transform"]["position"][2] + 0.1
                    ]
                    remove_edges(graph, obj)
                    add_edge(graph, obj["id"], "ON", counter["id"])
                    print(obj_name, ":", obj["id"])
  
        print("cabinet:", cabinet["id"], "kitchen:", kitchen_node["id"], "sink:", sink["id"], 
              "faucet:", faucet["id"], "counter:", counter["id"])

    else:
        return 0

    # Update the scene with new graph
    s, m = comm.expand_scene(graph)

    if s:
        # with open("updated_graph.json", "w") as f:
        #     json.dump(graph, f, indent=4)
        print("Scene expansion successful!")
    else:
        print("Scene expansion failed:", m)

    # Add human and robot
    comm.add_character_camera(position=[0, 5, 0], rotation=[90, 0, 0], name='global_top_view')
    comm.add_character('Chars/Male1', initial_room=spawn_locations[0])
    comm.add_character('Chars/Male2', initial_room=spawn_locations[1])

def generate_video_from_images(output_folder, i, round, output_video="output.mp4"):    
    image_pattern = os.path.join(output_folder, f"Action_%04d_{i}_normal.png")
    output_video_path = os.path.join(output_folder, f"{round}_{output_video}.mp4")

    ffmpeg_command = [
        "ffmpeg",
        "-framerate", "20",
        "-i", image_pattern,
        "-c:v", "libx264",
        "-r", "20",
        output_video_path
    ]

    try:
        print(f"Generating video from images in {output_folder}...")
        subprocess.run(ffmpeg_command, check=True)

        # Delete all images after video is created
        for file in os.listdir(output_folder):
            if file.startswith("Action_") and file.endswith("_0_normal.png"):
                os.remove(os.path.join(output_folder, file))

        print(f"Video saved as {output_video_path}")
        print("All images deleted successfully.")

    except subprocess.CalledProcessError as e:
        print(f"Error occurred while generating video: {e}")

def run_virtualhome_plan(plan, domain_name):
    print("Initializing VirtualHome...")

    comm = UnityCommunication()
    comm.reset(0)

    start_time = time.time()

    set_domain_graph(comm, domain_name)

    print(f"Running VirtualHome Plan:\n{plan}")
    comm.render_script(plan, recording=True, frame_rate=10, find_solution=True, 
                       randomize_execution=False, random_seed=42, camera_mode=['global_top_view'])
    
    end_time = time.time()

    print(f"Plan execution completed in {end_time - start_time:.2f} seconds.")
    print("Generated video in: simulation/unity_simulator/output/")

def main(json_file):
    with open(json_file, "r") as f:
        plans = json.load(f)

    plan_keys = [plan["round"] for plan in plans]

    print("\nAvailable VirtualHome Plans:")
    for idx, key in enumerate(plan_keys, 1):
        print(f"{idx}. {key}")

    choice = input("Select a plan to run (enter number): ").strip()

    if not choice.isdigit() or not (1 <= int(choice) <= len(plans)):
        print("Invalid selection!")
        return

    selected_index = int(choice) - 1
    selected_plan = plans[selected_index]

    domain_name="instance_wash_the_dishes"
    print(f"Running plan: {selected_plan['round']}")
    run_virtualhome_plan(selected_plan["script"], domain_name)

    generate_video_from_images(OUTPUT_PATH, 0, selected_index, domain_name)
    generate_video_from_images(OUTPUT_PATH_1, 0, selected_index, domain_name)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run_virtualhome.py <json_file>")
        sys.exit(1)

    main(sys.argv[1])

# Generate video for a program. Make sure you have the executable open, Commands to run virtualhome
# export PYTHONPATH=$PYTHONPATH:/home/ayush/iiith/RRC/Task_Planning/virtualhome-2.3.0/simulation/
# ayush@ayush-dell:~/iiith/RRC/Task_Planning/virtualhome-2.3.0/simulation/unity_simulator/Output/script/0$ ffmpeg -framerate 1 -i Action_%04d_0_normal.png -c:v libx264 -r 40 output.mp4
# ayush@ayush-dell:~/iiith/RRC/Task_Planning/virtualhome-2.3.0/simulation/unity_simulator$ ./linux_exec.v2.3.0.x86_64 -screen-fullscreen 0 -screen-quality 4
