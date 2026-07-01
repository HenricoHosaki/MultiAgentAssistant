import sys
import warnings

from sac_assistant.crews.products_crew.products_crew import ProductsCrew
from sac_assistant.flow import SacFlow

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def run():
    flow = SacFlow()
    flow.kickoff(inputs = {"question": "Do you offer a loyalty rewards program with points?"})
    print(flow.state.answer)

def train():
    inputs = {
        "question": "Is the backpack waterproof?"
    }
    try:
        ProductsCrew().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    try:
        ProductsCrew().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    inputs = {
        "question": "Is the backpack waterproof?"
    }

    try:
        ProductsCrew().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

def run_with_trigger():
    import json

    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")

    inputs = {
        "crewai_trigger_payload": trigger_payload,
        "question": ""
    }

    try:
        result = ProductsCrew().crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew with trigger: {e}")
