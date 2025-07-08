from llm_plan import *
from domain_eval import *

def simulate_plan(domain, plan, replan = False):
    if replan == True:
        domain.error_log = []
    parsed_plan = domain.parse_plan_string(plan)
    for i, line in enumerate(parsed_plan):
        action, args = domain.parse_line(line)
        print(action)
        if action in domain.actions:
            domain.actions[action](*args)
        failure, state, error = domain.update_world_state()
        print(state[-1])
        if failure:
            return False, i, parsed_plan, state[-1], error
    return True, len(parsed_plan), parsed_plan, state[-1], None

def run_plan_cycle(prompt, MAX_REPLANS = 3):
    session = ChatSession(save_dir="chat_logs/salmon_water")
    domain = HouseholdDomain()
    error_prompt = None
    replan = False
    action_count = 0

    for attempt in range(MAX_REPLANS + 1):
        if attempt == 0:
            output = session.ask_initial(prompt)  
        else:
            output = session.ask_reprompt(f"{error_prompt}")
                                 
        plan = session.parse_plan_from_output(output)
        print("=================================================================")
        print(plan)
        print("=================================================================")
        success, last_index, full_plan, state, errors = simulate_plan(domain, plan, replan)
        action_count += last_index

        if success:
            print("Action Count:", action_count)
            session.save_outputs()
            return 
        else:
            print("=================================================================")
            error_prompt = f"There was a failure while running the plan at action {full_plan[last_index]} \
                            due to: {errors}, with current state being {state}. \
                            Continue from that action and generate a plan."
            print(error_prompt)
            print("Action Count:", action_count)
            print("=================================================================")
            replan = True

    session.save_outputs()

task_prompts = get_task_prompts("Prepare Salmon", "Serve Water")
# Run a single plan
run_plan_cycle(general_description + task_prompts + output_format)



