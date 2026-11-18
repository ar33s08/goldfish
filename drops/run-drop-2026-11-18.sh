#!/bin/bash
# goldfish drop-1: 3 seeds vs production bot-farm endpoint (TensorFold pico-qwen38-tf)
cd "$HOME/goldfish"
URL="https://spark-fceb.tail391339.ts.net/v1"
MODEL="Qwen3.8-Flash-Next"
mkdir -p drops/2026-11-18
for seed in 1337 4242 9001; do
  echo "=== seed $seed start $(date -u +%FT%TZ)"
  .venv/bin/python -m goldfish.cli --base-url "$URL" --model "$MODEL" \
    --markers 12 --seed "$seed" --chunks 4 --turns-per-chunk 6 \
    --json "drops/2026-11-18/run-$seed.json" > "drops/2026-11-18/run-$seed.out" 2> "drops/2026-11-18/run-$seed.err"
  echo "=== seed $seed exit $? $(date -u +%FT%TZ)"
  tail -2 "drops/2026-11-18/run-$seed.out"
done
echo "ALL_DONE"
