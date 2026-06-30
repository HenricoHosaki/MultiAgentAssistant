import json
import os
from pathlib import Path

from datasets import Dataset
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import ChatOpenAI
from ragas import evaluate
from ragas.run_config import RunConfig
from ragas.metrics import answer_correctness, answer_relevancy, faithfulness

from sac_assistant.flow import SacFlow
from sac_assistant.rag.retriever import retrieve

load_dotenv()

GOLDEN_SET_PATH = Path(__file__).parent / "golden_set.jsonl"
RESULTS_PATH = Path(__file__).parent / "eval_results.csv"

# Judge LLM. Defaults to the same model the system uses (MODEL env, e.g. gpt-oss-120b) for
# simplicity — note this is a known limitation: a model grading answers from its own family
# shares the same blind spots. For a more independent eval, set EVAL_JUDGE_MODEL to a different
# (ideally stronger) model — then judge independence is one env var away without touching code.
JUDGE_MODEL = os.environ.get("EVAL_JUDGE_MODEL", os.environ["MODEL"].split("/", 1)[1])


def load_golden_set() -> list[dict]:
    with open(GOLDEN_SET_PATH, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def run_flow(question: str):
    flow = SacFlow()
    flow.kickoff(inputs={"question": question})
    return flow.state


def evaluate_answers(answer_items: list[dict]):
    """RAGAS quality metrics, scored ONLY on questions the system actually answered.

    Questions that should have been answered but escalated/refused instead are counted as a
    behavior miss and excluded from RAGAS, so a canned handoff message never pollutes the
    faithfulness/relevancy scores.
    """
    questions: list[str] = []
    answers: list[str] = []
    contexts: list[list[str]] = []
    references: list[str] = []
    behavior_hits = 0

    for i, item in enumerate(answer_items, start=1):
        print(f"[answer {i}/{len(answer_items)}] {item['question']!r}")
        state = run_flow(item["question"])

        if state.outcome != "answered":
            print(f"  [behavior MISS] outcome={state.outcome!r} (expected 'answered') — excluded from RAGAS")
            continue

        behavior_hits += 1
        results = retrieve(item["question"], collection_name=item["domain"])
        questions.append(item["question"])
        answers.append(state.answer)
        contexts.append(results["documents"][0])
        references.append(item["ground_truth"])

    behavior_accuracy = behavior_hits / len(answer_items) if answer_items else 0.0
    print(f"\nAnswer-behavior accuracy: {behavior_hits}/{len(answer_items)} = {behavior_accuracy:.2%}")

    if not questions:
        print("No answered questions to score with RAGAS.")
        return None, behavior_accuracy

    dataset = Dataset.from_dict(
        {
            "question": questions,
            "answer": answers,
            "contexts": contexts,
            "ground_truth": references,
        }
    )

    judge_llm = ChatOpenAI(
        model=JUDGE_MODEL,
        base_url="https://api.cerebras.ai/v1",
        api_key=os.environ["CEREBRAS_API_KEY"],
    )
    judge_embeddings = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=os.environ["GEMINI_API_KEY"],
    )

    # Low concurrency + generous timeout: the previous default (16 parallel workers) overwhelmed
    # the free-tier judge API and made answer_relevancy time out into NaN. Running a few jobs at
    # a time trades speed for actually getting every metric back.
    run_config = RunConfig(max_workers=3, timeout=300)

    result = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy, answer_correctness],
        llm=judge_llm,
        embeddings=judge_embeddings,
        run_config=run_config,
    )
    print(result)
    return result, behavior_accuracy


def evaluate_behavior(behavior_items: list[dict]) -> float:
    """For must-escalate / must-refuse questions: did the flow take the right action?

    These have no grounded answer to score for faithfulness — the right metric is simply
    whether the system escalated or refused as expected.
    """
    hits = 0
    for item in behavior_items:
        state = run_flow(item["question"])
        expected = item["expected_behavior"]
        ok = state.outcome == expected
        hits += int(ok)
        flag = "OK" if ok else "MISS"
        print(f"  [{flag}] {item['question']!r} -> outcome={state.outcome!r} (expected {expected!r})")

    accuracy = hits / len(behavior_items) if behavior_items else 0.0
    print(f"\nEscalate/Refuse behavior accuracy: {hits}/{len(behavior_items)} = {accuracy:.2%}")
    return accuracy


def run() -> None:
    golden_set = load_golden_set()
    answer_items = [g for g in golden_set if g["expected_behavior"] == "answer"]
    behavior_items = [g for g in golden_set if g["expected_behavior"] in ("escalate", "refuse")]

    print(f"=== Answer questions ({len(answer_items)}) — RAGAS quality ===")
    rag_result, answer_behavior_acc = evaluate_answers(answer_items)

    print(f"\n=== Escalate/Refuse questions ({len(behavior_items)}) — behavior only ===")
    behavior_acc = evaluate_behavior(behavior_items)

    if rag_result is not None:
        df = rag_result.to_pandas()
        df.to_csv(RESULTS_PATH, index=False)
        print(f"\nSaved detailed RAGAS results to {RESULTS_PATH}")

    print("\n=== Summary ===")
    print(f"Answer-behavior accuracy (answered when it should): {answer_behavior_acc:.2%}")
    print(f"Escalate/Refuse accuracy (right action taken):      {behavior_acc:.2%}")
    if rag_result is not None:
        print(f"RAGAS quality: {rag_result}")


if __name__ == "__main__":
    run()
