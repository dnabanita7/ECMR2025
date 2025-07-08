# Anticipate-Adapt-Act
A Hybrid LLM + RDDL Planner for Robust Human–Robot Collaboration

This repository accompanies the ECMR-2025 paper  
**“Anticipate, Adapt, Act: A Hybrid LLM–RDDL Framework for Failure-Aware Human-Robot Assistance.”**

The system:

1. Anticipates upcoming human-robot subtasks with an LLM (Groq / GPT-class).
2. Translates these into RDDL goals and generates robust plans with PROST.
3. Executes and recovers inside the VirtualHome-3D household simulator.
4. Logs success, recovery count, and action efficiency for benchmarking.

---

## Directory Layout

code/
├── jsonfiles/ # prompts, task lists, mappings 

├── rddl/ # domain templates + hand-written instances

├── generated_instances/ # auto-generated instances (ours)

├── generated_instances_baseline/

├── outputs/ # plans, logs, metrics

├── *.py # pipeline scripts (see below)

└── requirements.txt # minimal PyPI deps



1. **Prerequisites**
   - Python ≥ 3.9
   - VirtualHome 2.2.0 (Unity)
   - PROST (commit 2024-05-23)
   - Groq / OpenAI API key (GPT-3.5/4)
   - Optional: ffmpeg (for video export)

2. **Quick Start**
   1. Clone repository and enter `code/`
   2. Create and activate virtual environment  
      `python -m venv venv && source venv/bin/activate`
   3. Install dependencies  
      `pip install -r requirements.txt`  
      `pip install numpy python-dotenv`
   4. Add LLM credentials in `.env`  
      `GROQ_API_KEY=<your-key>` (or `OPENAI_API_KEY`)
   5. Install VirtualHome (Unity build path = `<VH_SIM>`)
   6. Build PROST (`~/prost`)
   7. Edit hard-coded paths in:
      - `run_virtualhome.py`
      - `run_llm_pipeline.py`
   8. Run pipeline:
      ```bash
      python llm_task_handler.py
      python create_instances.py
      python run_llm_pipeline.py
      python translate_rddl_to_virtualhome.py
      python run_virtualhome.py
      ```

3. **Script Overview**
   - `llm_task_handler.py` &nbsp;→ anticipates tasks with LLM  
   - `create_instances.py` &nbsp;→ fills RDDL templates  
   - `run_llm_pipeline.py` &nbsp;→ runs PROST planner  
   - `translate_rddl_to_virtualhome.py` &nbsp;→ converts plans  
   - `run_virtualhome.py` &nbsp;→ executes in simulator  
   - `simulate_tasks.py` &nbsp;→ robustness roll-outs  
   - `evaluate_baseline_wrt_ours.py` &nbsp;→ paper metrics

4. **Configuration Files**
   - `jsonfiles/master_tasks.json` – seed vocabulary  
   - `jsonfiles/llm_tasks.json` – generated tasks per run  
   - `jsonfiles/rddl_goals.json` – LLM-to-RDDL mapping  
   - `rddl/domain_x_robot_anticipation.rddl` – main domain  
   - Additional `.rddl` files – toy/baseline domains

5. **Reproduce Paper Metrics**
   #### Completion
   python evaluate_baseline_wrt_ours.py --metric success
   #### Recovery
   python evaluate_baseline_wrt_ours.py --metric recovery
   #### Efficiency
   python evaluate_baseline_wrt_ours.py --metric actions


6. **Customising**
   - **LLM model**  
     Switch from Groq to OpenAI by exporting `OPENAI_API_KEY` and replacing the client in `llm_task_handler.py`:

     ```python
     from openai import OpenAI
     ...
     client = OpenAI()   # instead of Groq()
     ```

   - **Simulator path**  
     Edit `VH_SIM_PATH` in `run_virtualhome.py`:

     ```python
     VH_SIM_PATH = os.environ.get(
         "VIRTUALHOME_SIM",
         "/abs/path/to/virtualhome/simulation/"
     )
     ```

   - **PROST location**  
     `run_llm_pipeline.py` assumes:

     ```python
     prost_testbed_dir = os.path.expanduser("~/prost/testbed")
     prost_dir        = os.path.expanduser("~/prost")
     ```

     Change these variables if your PROST build lives elsewhere.

---

7. **Troubleshooting**

| Issue                                   | Remedy                                                                                                   |
|-----------------------------------------|-----------------------------------------------------------------------------------------------------------|
| `UnityCommunication` import error       | Verify `VH_SIM_PATH` and run `pip install -e virtualhome/simulation`.                                     |
| PROST stalls at 0 %                     | Increase the `time.sleep()` delay in `run_llm_pipeline.py` (slow disks or heavy instances).               |
| LLM quota reached or rate-limit errors  | Reduce the task list in `jsonfiles/llm_tasks.json` while debugging, or cache responses in `outputs/`.     |
| Simulator crashes mid-run               | Check Unity build version, GPU drivers, and ensure the correct scene name in `run_virtualhome.py`.        |

---

8. **Licence**

| Asset                 | Licence               |
|-----------------------|-----------------------|
| Code and scripts      | MIT                   |
| RDDL domain text      | CC BY-NC-SA 4.0       |
| VirtualHome assets    | Apache-2.0 (upstream) |

