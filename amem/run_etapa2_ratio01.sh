#!/usr/bin/env bash
set -euo pipefail

if [[ -f .env.local ]]; then
  set -a
  source .env.local
  set +a
fi

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  echo "OPENAI_API_KEY is not set." >&2
  exit 2
fi

export HF_HOME="${HF_HOME:-.cache/huggingface}"
export MPLCONFIGDIR="${MPLCONFIGDIR:-.cache/matplotlib}"
export NLTK_DATA="${NLTK_DATA:-.cache/nltk}"

mkdir -p results logs commands analysis "$HF_HOME" "$MPLCONFIGDIR" "$NLTK_DATA"

for k in 3 5 10; do
  /usr/bin/time -p .venv/bin/python test_advanced_robust.py \
    --backend openai \
    --model gpt-4o-mini \
    --dataset data/locomo10.json \
    --ratio 0.1 \
    --retrieve_k "$k" \
    --seed 0 \
    --temperature 0.0 \
    --output "results/results_amem_gpt4omini_ratio01_k${k}.json"
done
