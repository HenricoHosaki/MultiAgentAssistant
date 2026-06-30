import json
import os
from pathlib import Path

from datasets import Dataset
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import ChatOpenAI
from ragas import evaluate
from ragas.metrics import answer_relevancy, faithfulness

from sac_assistant.flow import SacFlow
from sac_assistant.rag.retriever import retrieve

load_dotenv()

GOLDEN_SET_PATH = Path(__file__).parent / "golden_set.jsonl"
RESULTS_PATH = Path(__file__).parent / "eval_results.csv"

RAG_DOMAINS = {"products", "delivery", "payments"}


def load_golden_set() -> list[dict]:
    with open(GOLDEN_SET_PATH, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def build_dataset() -> Dataset:
    golden_set = load_golden_set()

    questions: list[str] = []
    answers: list[str] = []
    contexts: list[list[str]] = []

    for i, item in enumerate(golden_set, start=1):
        question = item["question"]
        domain = item["domain"]
        print(f"[{i}/{len(golden_set)}] Running: {question!r} (domain={domain})")

        flow = SacFlow()
        flow.kickoff(inputs={"question": question})
        answer = flow.state.answer

        if domain in RAG_DOMAINS:
            results = retrieve(question, collection_name=domain)
            retrieved_chunks = results["documents"][0]
        else:
            retrieved_chunks = []

        questions.append(question)
        answers.append(answer)
        contexts.append(retrieved_chunks)

    return Dataset.from_dict(
        {
            "question": questions,
            "answer": answers,
            "contexts": contexts,
        }
    )


def run() -> None:
    dataset = build_dataset()

    judge_llm = ChatOpenAI(
        model=os.environ["MODEL"].split("/", 1)[1],
        base_url="https://api.cerebras.ai/v1",
        api_key=os.environ["CEREBRAS_API_KEY"],
    )
    judge_embeddings = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=os.environ["GEMINI_API_KEY"],
    )

    result = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy],
        llm=judge_llm,
        embeddings=judge_embeddings,
    )

    print(result)
    df = result.to_pandas()
    df.to_csv(RESULTS_PATH, index=False)
    print(f"\nSaved detailed results to {RESULTS_PATH}")


if __name__ == "__main__":
    run()
