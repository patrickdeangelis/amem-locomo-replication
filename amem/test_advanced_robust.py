"""
Evaluation harness using the robust memory layer (no JSON schema dependency).
Drop-in replacement for test_advanced.py.

Usage:
    python test_advanced_robust.py --backend openai --model gpt-4o-mini --dataset data/locomo10.json
    python test_advanced_robust.py --backend ollama --model qwen2.5:3b --dataset data/locomo10.json
"""

from memory_layer_robust import RobustLLMController, RobustAgenticMemorySystem
from llm_text_parsers import (
    parse_plain_text_answer,
    parse_relevant_parts,
    parse_keywords_response,
)
import os
import sys
import json
import argparse
import logging
import hashlib
import platform
import re
import subprocess
import time
from typing import Any, List, Dict, Optional
from pathlib import Path
import numpy as np
from load_dataset import load_locomo_dataset, QA, Turn, Session, Conversation
import nltk
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import pytorch_cos_sim
import statistics
from collections import defaultdict
import pickle
import random
from tqdm import tqdm
from utils import calculate_metrics, aggregate_metrics
from datetime import datetime, timezone


USAGE_COUNTER_KEYS = (
    "requests",
    "attempts_total",
    "failed_attempts",
    "input_tokens",
    "cached_input_tokens",
    "output_tokens",
    "total_tokens",
)
USAGE_PRICING_USD_PER_MILLION = {
    "input_tokens": 0.15,
    "cached_input_tokens": 0.075,
    "output_tokens": 0.60,
}
USAGE_PRICING_METADATA = {
    "as_of": "2026-07-14",
    "currency": "USD",
    "source_url": "https://openai.com/api/pricing/",
}


def combine_usage_snapshots(
    snapshots: List[Dict], model: Optional[str] = None
) -> Dict:
    """Sum usage snapshots without retaining request content or credentials."""
    combined = {key: 0 for key in USAGE_COUNTER_KEYS}
    for snapshot in snapshots:
        for key in USAGE_COUNTER_KEYS:
            combined[key] += snapshot.get(key, 0) or 0
        if model is None and snapshot.get("model"):
            model = snapshot["model"]
    return {**combined, "model": model}


def diff_usage_snapshots(after: Dict, before: Dict) -> Dict:
    """Return usage accrued between two cumulative snapshots."""
    return {
        **{key: (after.get(key, 0) or 0) - (before.get(key, 0) or 0)
           for key in USAGE_COUNTER_KEYS},
        "model": after.get("model") or before.get("model"),
    }


def estimate_usage_cost_usd(snapshot: Dict) -> float:
    """Estimate OpenAI cost using the experiment's explicit price snapshot."""
    cached = snapshot.get("cached_input_tokens", 0) or 0
    input_tokens = snapshot.get("input_tokens", 0) or 0
    uncached = max(0, input_tokens - cached)
    output = snapshot.get("output_tokens", 0) or 0
    return (
        uncached * USAGE_PRICING_USD_PER_MILLION["input_tokens"]
        + cached * USAGE_PRICING_USD_PER_MILLION["cached_input_tokens"]
        + output * USAGE_PRICING_USD_PER_MILLION["output_tokens"]
    ) / 1_000_000


def build_run_tracking_metadata(
    replicate_id: Optional[str],
    schedule_seed: Optional[int],
    cache_namespace: Optional[str],
    memory_build: Dict,
    evaluation: Dict,
    schedule_position: Optional[int] = None,
    sample_ids: Optional[List[int]] = None,
) -> Dict:
    """Build serializable run identity, phase usage, and estimated costs."""
    total = combine_usage_snapshots(
        [memory_build, evaluation], model=memory_build.get("model") or evaluation.get("model")
    )

    def with_cost(snapshot: Dict) -> Dict:
        return {**snapshot, "estimated_cost_usd": estimate_usage_cost_usd(snapshot)}

    return {
        "replicate_id": replicate_id,
        "schedule_seed": schedule_seed,
        "schedule_position": schedule_position,
        "cache_namespace": cache_namespace,
        "sample_ids": list(sample_ids or []),
        "usage": {
            "pricing_usd_per_million": dict(USAGE_PRICING_USD_PER_MILLION),
            "pricing_metadata": dict(USAGE_PRICING_METADATA),
            "memory_build": with_cost(memory_build),
            "evaluation": with_cost(evaluation),
            "total": with_cost(total),
        },
    }


def sha256_of_file(path: str, chunk: int = 1 << 20) -> str:
    """Compute sha256 hex digest of a file, reading in chunks."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def git_commit_sha(repo_dir: str) -> Optional[str]:
    """Return current git commit SHA of repo_dir, or None if not a git repo."""
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_dir,
            stderr=subprocess.DEVNULL,
        )
        return out.decode().strip()
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return None


def git_worktree_provenance(repo_dir: str) -> Dict[str, Any]:
    """Describe the worktree and hash the code paths that drive evaluation."""
    try:
        status = subprocess.check_output(
            ["git", "status", "--porcelain=v1", "--untracked-files=all"],
            cwd=repo_dir,
            stderr=subprocess.DEVNULL,
        )
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        status = b""
    code_paths = (
        "test_advanced_robust.py",
        "memory_layer_robust.py",
        "utils.py",
        "llm_text_parsers.py",
        "load_dataset.py",
        "run_entrega3.py",
        "analysis/result_validation.py",
    )
    hashes = {
        path: sha256_of_file(os.path.join(repo_dir, path))
        for path in code_paths
        if os.path.isfile(os.path.join(repo_dir, path))
    }
    return {
        "git_dirty": bool(status.strip()),
        "git_status_sha256": hashlib.sha256(status).hexdigest(),
        "code_sha256": hashes,
    }


def resolve_memories_dir(
    backend: str,
    model: str,
    dataset_path: str,
    cache_namespace: Optional[str] = None,
) -> str:
    """Resolve the cache directory for cached memories.

    Uses a hash-suffixed directory name so that renaming a dataset file (while
    keeping its stem) cannot silently reuse a cache built for different content.

    For backward compatibility with caches created by the previous naming scheme
    (stem-only), if the hash-suffixed directory does not exist but a legacy
    stem-only directory does exist, the legacy directory is adopted: the current
    dataset hash is recorded inside it and the legacy path is returned. If the
    legacy directory already records a hash that does not match the current
    dataset, the hash-suffixed directory is used instead (forcing a fresh cache).
    """
    base = os.path.dirname(__file__)
    dataset_stem = Path(dataset_path).stem
    dataset_hash = sha256_of_file(dataset_path)
    hash12 = dataset_hash[:12]

    hash_dir = os.path.join(
        base, f"cached_memories_robust_{backend}_{model}_{dataset_stem}_{hash12}"
    )
    if cache_namespace is not None:
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", cache_namespace):
            raise ValueError(
                "Invalid cache namespace: use 1-64 letters, digits, dots, underscores, or hyphens"
            )
        namespaced_dir = f"{hash_dir}_ns-{cache_namespace}"
        os.makedirs(namespaced_dir, exist_ok=True)
        return namespaced_dir

    legacy_dir = os.path.join(
        base, f"cached_memories_robust_{backend}_{model}_{dataset_stem}"
    )
    hash_marker = os.path.join(legacy_dir, "dataset_hash.txt")

    if os.path.isdir(hash_dir):
        return hash_dir

    if os.path.isdir(legacy_dir):
        if os.path.isfile(hash_marker):
            recorded = Path(hash_marker).read_text(encoding="utf-8").strip()
            if recorded == dataset_hash:
                return legacy_dir
            # Hash mismatch -> fall through to hash_dir (fresh cache).
        else:
            # Legacy cache without a hash marker: adopt it for the current dataset.
            try:
                Path(hash_marker).write_text(dataset_hash, encoding="utf-8")
            except OSError:
                pass
            return legacy_dir

    os.makedirs(hash_dir, exist_ok=True)
    return hash_dir


# Download required NLTK data
for resource_path, resource_name in (
    ("tokenizers/punkt", "punkt"),
    ("tokenizers/punkt_tab/english", "punkt_tab"),
    ("corpora/wordnet", "wordnet"),
):
    try:
        nltk.data.find(resource_path)
    except LookupError:
        nltk.download(resource_name)

# Initialize SentenceTransformer model (this will be reused)
try:
    sentence_model = SentenceTransformer("all-MiniLM-L6-v2")
except Exception as e:
    print(f"Warning: Could not load SentenceTransformer model: {e}")
    sentence_model = None

logger = logging.getLogger("amem_robust")


class RobustAdvancedMemAgent:
    """Agent using the robust memory system with plain-text LLM calls."""

    def __init__(
        self,
        model,
        backend,
        retrieve_k,
        temperature_c5,
        temperature_answer=0.7,
        rng: Optional[random.Random] = None,
        sglang_host="http://localhost",
        sglang_port=30000,
    ):
        self.memory_system = RobustAgenticMemorySystem(
            model_name="all-MiniLM-L6-v2",
            llm_backend=backend,
            llm_model=model,
            sglang_host=sglang_host,
            sglang_port=sglang_port,
        )
        self.retriever_llm = RobustLLMController(
            backend=backend,
            model=model,
            api_key=None,
            sglang_host=sglang_host,
            sglang_port=sglang_port,
        )
        self.retrieve_k = retrieve_k
        self.temperature_c5 = temperature_c5
        # Temperature for categories 1-4. Set to 0.0 for reproducible evaluation.
        self.temperature_answer = temperature_answer
        # Category 5 uses a coin flip to decide answer ordering. A seeded RNG
        # makes that flip reproducible instead of relying on global random state.
        self.rng = rng if rng is not None else random.Random()

    def add_memory(self, content, time=None):
        self.memory_system.add_note(content, time=time)

    def retrieve_memory(self, content, k=10):
        return self.memory_system.find_related_memories_raw(content, k=k)

    def retrieve_memory_llm(self, memories_text, query):
        """Select relevant parts of conversation memories — plain text, no JSON schema."""
        prompt = f"""Given the following conversation memories and a question, select the most relevant parts of the conversation that would help answer the question. Include the date/time if available.

Conversation memories:
{memories_text}

Question: {query}

Return only the relevant parts of the conversation that would help answer this specific question.
If no parts are relevant, return the input unchanged."""

        response = self.retriever_llm.llm.get_completion(prompt)
        return parse_relevant_parts(response)

    def generate_query_llm(self, question):
        """Generate query keywords — plain text, no JSON schema."""
        prompt = f"""Given the following question, generate several keywords separated by commas.

Question: {question}

Keywords:"""

        response = self.retriever_llm.llm.get_completion(prompt)
        result = parse_keywords_response(response)
        logger.debug("generate_query_llm response: %s", result)
        return result

    def answer_question(self, question: str, category: int, answer: str) -> tuple:
        """Generate answer for a question — plain text, no JSON schema."""
        keywords = self.generate_query_llm(question)
        raw_context = self.retrieve_memory(keywords, k=self.retrieve_k)
        context = raw_context

        assert category in [1, 2, 3, 4, 5]

        if category == 5:
            answer_tmp = list()
            if self.rng.random() < 0.5:
                answer_tmp.append("Not mentioned in the conversation")
                answer_tmp.append(answer)
            else:
                answer_tmp.append(answer)
                answer_tmp.append("Not mentioned in the conversation")
            user_prompt = f"""Based on the context: {context}, answer the following question. {question}

Select the correct answer: {answer_tmp[0]} or {answer_tmp[1]}  Short answer:"""
            temperature = self.temperature_c5
        elif category == 2:
            user_prompt = f"""Based on the context: {context}, answer the following question. Use DATE of CONVERSATION to answer with an approximate date.
Please generate the shortest possible answer, using words from the conversation where possible, and avoid using any subjects.

Question: {question} Short answer:"""
            temperature = self.temperature_answer
        elif category == 3:
            user_prompt = f"""Based on the context: {context}, write an answer in the form of a short phrase for the following question. Answer with exact words from the context whenever possible.

Question: {question} Short answer:"""
            temperature = self.temperature_answer
        else:
            user_prompt = f"""Based on the context: {context}, write an answer in the form of a short phrase for the following question. Answer with exact words from the context whenever possible.

Question: {question} Short answer:"""
            temperature = self.temperature_answer

        try:
            response = self.memory_system.llm_controller.llm.get_completion(
                user_prompt,
                temperature=temperature,
            )
        except Exception as e:
            logger.warning("answer_question failed: %s — returning empty", e)
            response = ""
        return response, user_prompt, raw_context


def get_agent_usage_snapshot(agent: RobustAdvancedMemAgent, model: str) -> Dict:
    """Combine usage from the memory and retrieval OpenAI controllers."""
    controllers = (
        agent.memory_system.llm_controller.llm,
        agent.retriever_llm.llm,
    )
    snapshots = []
    for controller in controllers:
        get_snapshot = getattr(controller, "get_usage_snapshot", None)
        if get_snapshot is not None:
            snapshots.append(get_snapshot())
    return combine_usage_snapshots(snapshots, model=model)


def setup_logger(log_file: Optional[str] = None) -> logging.Logger:
    """Set up logging configuration."""
    eval_logger = logging.getLogger("locomo_eval_robust")
    eval_logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    eval_logger.addHandler(console_handler)

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        eval_logger.addHandler(file_handler)

    return eval_logger


def evaluate_dataset(
    dataset_path: str,
    model: str,
    output_path: Optional[str] = None,
    ratio: float = 1.0,
    backend: str = "sglang",
    temperature_c5: float = 0.5,
    retrieve_k: int = 10,
    seed: int = 0,
    temperature_answer: float = 0.7,
    sglang_host: str = "http://localhost",
    sglang_port: int = 30000,
    replicate_id: Optional[str] = None,
    schedule_seed: Optional[int] = None,
    cache_namespace: Optional[str] = None,
    schedule_position: Optional[int] = None,
):
    """Evaluate the robust agent on the LoComo dataset."""
    # Seed RNGs for reproducibility. Category 5's answer-ordering coin flip and
    # any other random behavior become deterministic for a given seed.
    random.seed(seed)
    np.random.seed(seed)
    eval_rng = random.Random(seed)

    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
    timestamp_start_iso = datetime.now(timezone.utc).isoformat()
    wall_start = time.time()
    log_filename = f"eval_robust_{model}_{backend}_ratio{ratio}_{timestamp}.log"
    log_path = os.path.join(os.path.dirname(__file__), "logs", log_filename)
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    eval_logger = setup_logger(log_path)
    eval_logger.info(f"Loading dataset from {dataset_path}")
    eval_logger.info(f"Using ROBUST memory layer (no JSON schema dependency)")
    eval_logger.info(
        f"Reproducibility: seed={seed} temperature_answer={temperature_answer} "
        f"temperature_c5={temperature_c5} retrieve_k={retrieve_k}"
    )

    samples = load_locomo_dataset(dataset_path)
    eval_logger.info(f"Loaded {len(samples)} samples")

    if ratio < 1.0:
        num_samples = max(1, int(len(samples) * ratio))
        samples = samples[:num_samples]
        eval_logger.info(f"Using {num_samples} samples ({ratio * 100:.1f}% of dataset)")

    results = []
    all_metrics = []
    all_categories = []
    total_questions = 0
    category_counts = defaultdict(int)
    memory_build_usage = combine_usage_snapshots([], model=model)
    evaluation_usage = combine_usage_snapshots([], model=model)
    selected_sample_ids = []

    i = 0
    error_num = 0
    memories_dir = resolve_memories_dir(
        backend, model, dataset_path, cache_namespace=cache_namespace
    )
    os.makedirs(memories_dir, exist_ok=True)
    allow_categories = [1, 2, 3, 4, 5]

    for sample_idx, sample in enumerate(samples):
        selected_sample_ids.append(sample_idx)
        agent = RobustAdvancedMemAgent(
            model,
            backend,
            retrieve_k,
            temperature_c5,
            temperature_answer=temperature_answer,
            rng=eval_rng,
            sglang_host=sglang_host,
            sglang_port=sglang_port,
        )
        usage_before_memory_build = get_agent_usage_snapshot(agent, model)

        memory_cache_file = os.path.join(
            memories_dir, f"memory_cache_sample_{sample_idx}.pkl"
        )
        retriever_cache_file = os.path.join(
            memories_dir, f"retriever_cache_sample_{sample_idx}.pkl"
        )
        retriever_cache_embeddings_file = os.path.join(
            memories_dir, f"retriever_cache_embeddings_sample_{sample_idx}.npy"
        )

        if os.path.exists(memory_cache_file):
            eval_logger.info(f"Loading cached memories for sample {sample_idx}")
            with open(memory_cache_file, "rb") as f:
                cached_memories = pickle.load(f)
            agent.memory_system.memories = cached_memories
            if os.path.exists(retriever_cache_file):
                eval_logger.info(f"Found retriever cache files")
                agent.memory_system.retriever = agent.memory_system.retriever.load(
                    retriever_cache_file, retriever_cache_embeddings_file
                )
            else:
                eval_logger.info(f"No retriever cache found, loading from memory")
                agent.memory_system.retriever = (
                    agent.memory_system.retriever.load_from_local_memory(
                        cached_memories, "all-MiniLM-L6-v2"
                    )
                )
            eval_logger.info(f"Successfully loaded {len(cached_memories)} memories")
        else:
            eval_logger.info(
                f"No cached memories found for sample {sample_idx}. Creating new memories."
            )

            for _, turns in sample.conversation.sessions.items():
                for turn in turns.turns:
                    turn_datatime = turns.date_time
                    conversation_tmp = "Speaker " + turn.speaker + "says : " + turn.text
                    agent.add_memory(conversation_tmp, time=turn_datatime)

            memories_to_cache = agent.memory_system.memories
            with open(memory_cache_file, "wb") as f:
                pickle.dump(memories_to_cache, f)
            agent.memory_system.retriever.save(
                retriever_cache_file, retriever_cache_embeddings_file
            )
            eval_logger.info(f"Successfully cached {len(memories_to_cache)} memories")

        usage_after_memory_build = get_agent_usage_snapshot(agent, model)
        memory_build_usage = combine_usage_snapshots(
            [
                memory_build_usage,
                diff_usage_snapshots(
                    usage_after_memory_build, usage_before_memory_build
                ),
            ],
            model=model,
        )
        usage_before_evaluation = usage_after_memory_build

        eval_logger.info(f"Processing sample {sample_idx + 1}/{len(samples)}")

        for qa in sample.qa:
            if int(qa.category) in allow_categories:
                total_questions += 1
                category_counts[qa.category] += 1

                prediction, user_prompt, raw_context = agent.answer_question(
                    qa.question, qa.category, qa.final_answer
                )

                # Parse the prediction (handles both JSON and plain text)
                prediction = parse_plain_text_answer(prediction)

                eval_logger.info(f"Question {total_questions}: {qa.question}")
                eval_logger.info(f"Prediction: {prediction}")
                eval_logger.info(f"Reference: {qa.final_answer}")
                eval_logger.info(f"User Prompt: {user_prompt}")
                eval_logger.info(f"Category: {qa.category}")
                eval_logger.info(f"Raw Context: {raw_context}")

                metrics = (
                    calculate_metrics(prediction, qa.final_answer)
                    if qa.final_answer
                    else {
                        "exact_match": 0,
                        "f1": 0.0,
                        "rouge1_f": 0.0,
                        "rouge2_f": 0.0,
                        "rougeL_f": 0.0,
                        "bleu1": 0.0,
                        "bleu2": 0.0,
                        "bleu3": 0.0,
                        "bleu4": 0.0,
                        "bert_f1": 0.0,
                        "meteor": 0.0,
                        "sbert_similarity": 0.0,
                    }
                )

                all_metrics.append(metrics)
                all_categories.append(qa.category)

                result = {
                    "sample_id": sample_idx,
                    "question": qa.question,
                    "prediction": prediction,
                    "reference": qa.final_answer,
                    "category": qa.category,
                    "metrics": metrics,
                }
                results.append(result)

                if total_questions % 10 == 0:
                    eval_logger.info(f"Processed {total_questions} questions")

        usage_after_evaluation = get_agent_usage_snapshot(agent, model)
        evaluation_usage = combine_usage_snapshots(
            [
                evaluation_usage,
                diff_usage_snapshots(
                    usage_after_evaluation, usage_before_evaluation
                ),
            ],
            model=model,
        )

    aggregate_results = aggregate_metrics(all_metrics, all_categories)

    wall_end = time.time()
    timestamp_end_iso = datetime.now(timezone.utc).isoformat()
    duration_seconds = round(wall_end - wall_start, 3)

    # Provenance metadata so the output JSON is self-describing and auditable
    # without relying on external manifests. Reproducibility-relevant fields:
    # seed, temperatures, retrieve_k, dataset hash/size, code commit, command.
    repo_dir = os.path.dirname(__file__)
    dataset_abs = (
        os.path.join(repo_dir, dataset_path)
        if not os.path.isabs(dataset_path)
        else dataset_path
    )
    command_invocation = " ".join(sys.argv)
    metadata = {
        "schema_version": 1,
        "timestamp_start_utc": timestamp_start_iso,
        "timestamp_end_utc": timestamp_end_iso,
        "duration_seconds": duration_seconds,
        "seed": seed,
        "temperature_answer": temperature_answer,
        "temperature_c5": temperature_c5,
        "retrieve_k": retrieve_k,
        "ratio": ratio,
        "backend": backend,
        "model": model,
        "dataset_path": dataset_path,
        "dataset_stem": Path(dataset_path).stem,
        "dataset_sha256": sha256_of_file(dataset_abs),
        "dataset_size_bytes": os.path.getsize(dataset_abs),
        "memory_layer": "robust",
        "memories_cache_dir": os.path.relpath(memories_dir, repo_dir),
        "repo_commit": git_commit_sha(repo_dir),
        "repo_commit_role": "upstream base commit; exact local code is identified by code_sha256",
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "command": command_invocation,
    }
    metadata.update(git_worktree_provenance(repo_dir))
    metadata.update(
        build_run_tracking_metadata(
            replicate_id=replicate_id,
            schedule_seed=schedule_seed,
            cache_namespace=cache_namespace,
            memory_build=memory_build_usage,
            evaluation=evaluation_usage,
            schedule_position=schedule_position,
            sample_ids=selected_sample_ids,
        )
    )
    eval_logger.info(
        f"Run finished in {duration_seconds}s "
        f"(seed={seed}, dataset_sha256={metadata['dataset_sha256'][:12]})"
    )

    final_results = {
        "model": model,
        "dataset": dataset_path,
        "memory_layer": "robust",
        "total_questions": total_questions,
        "category_distribution": {
            str(cat): count for cat, count in category_counts.items()
        },
        "metadata": metadata,
        "aggregate_metrics": aggregate_results,
        "individual_results": results,
    }
    eval_logger.info(f"Error number: {error_num}")

    if output_path:
        with open(output_path, "w") as f:
            json.dump(final_results, f, indent=2)
        eval_logger.info(f"Results saved to {output_path}")

    eval_logger.info("Evaluation Summary:")
    eval_logger.info(f"Total questions evaluated: {total_questions}")
    eval_logger.info("Category Distribution:")
    for category, count in sorted(category_counts.items()):
        eval_logger.info(
            f"Category {category}: {count} questions ({count / total_questions * 100:.1f}%)"
        )

    eval_logger.info("Aggregate Metrics:")
    for split_name, metrics in aggregate_results.items():
        eval_logger.info(f"{split_name.replace('_', ' ').title()}:")
        for metric_name, stats in metrics.items():
            eval_logger.info(f"  {metric_name}:")
            for stat_name, value in stats.items():
                eval_logger.info(f"    {stat_name}: {value:.4f}")

    return final_results


def build_argument_parser() -> argparse.ArgumentParser:
    """Build the CLI parser without executing an experiment."""
    parser = argparse.ArgumentParser(
        description="Evaluate robust text-only agent on LoComo dataset (no JSON schema dependency)"
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default="data/locomo10.json",
        help="Path to the dataset file",
    )
    parser.add_argument("--model", type=str, default="gpt-4o-mini", help="Model to use")
    parser.add_argument(
        "--output", type=str, default=None, help="Path to save evaluation results"
    )
    parser.add_argument(
        "--ratio",
        type=float,
        default=1.0,
        help="Ratio of dataset to evaluate (0.0 to 1.0)",
    )
    parser.add_argument(
        "--backend",
        type=str,
        default="openai",
        help="Backend to use (openai, ollama, sglang, or vllm)",
    )
    parser.add_argument(
        "--temperature_c5",
        type=float,
        default=0.5,
        help="Temperature for category 5 questions",
    )
    parser.add_argument(
        "--retrieve_k", type=int, default=10, help="Number of memories to retrieve"
    )
    parser.add_argument(
        "--sglang_host",
        type=str,
        default="http://localhost",
        help="SGLang server host (for sglang backend)",
    )
    parser.add_argument(
        "--sglang_port",
        type=int,
        default=30000,
        help="SGLang server port (for sglang backend)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=0,
        help="Random seed for reproducibility (seeds Python random and numpy).",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help=(
            "Sampling temperature for answer generation (categories 1-4). "
            "Set to 0.0 for reproducible evaluation. Does NOT affect category 5, "
            "which is controlled by --temperature_c5."
        ),
    )
    parser.add_argument(
        "--replicate-id",
        type=str,
        default=None,
        help="Identifier for this experimental replicate.",
    )
    parser.add_argument(
        "--schedule-seed",
        type=int,
        default=None,
        help="Seed used to generate the external execution schedule.",
    )
    parser.add_argument(
        "--cache-namespace",
        type=str,
        default=None,
        help="Safe namespace that isolates the memory cache for this block.",
    )
    parser.add_argument(
        "--schedule-position",
        type=int,
        default=None,
        help="One-based position of this run in its replicate schedule.",
    )
    return parser


def main():
    parser = build_argument_parser()
    args = parser.parse_args()

    if args.ratio <= 0.0 or args.ratio > 1.0:
        raise ValueError("Ratio must be between 0.0 and 1.0")

    dataset_path = os.path.join(os.path.dirname(__file__), args.dataset)
    output_path = (
        os.path.join(os.path.dirname(__file__), args.output) if args.output else None
    )

    evaluate_dataset(
        dataset_path=dataset_path,
        model=args.model,
        output_path=output_path,
        ratio=args.ratio,
        backend=args.backend,
        temperature_c5=args.temperature_c5,
        retrieve_k=args.retrieve_k,
        seed=args.seed,
        temperature_answer=args.temperature,
        sglang_host=args.sglang_host,
        sglang_port=args.sglang_port,
        replicate_id=args.replicate_id,
        schedule_seed=args.schedule_seed,
        cache_namespace=args.cache_namespace,
        schedule_position=args.schedule_position,
    )


if __name__ == "__main__":
    main()
