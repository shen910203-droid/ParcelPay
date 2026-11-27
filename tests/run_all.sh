#!/bin/bash
# 用法：在 repo 根目錄執行  bash tests/run_all.sh
# 需要：python3、playwright（pip install playwright && python -m playwright install chromium）、Pillow
cd "$(dirname "$0")/.."
python3 -m http.server 8765 >/dev/null 2>&1 &
SRV=$!; sleep 1.5
for t in tests/test_*.py; do
  echo "===== $t"
  timeout 180 python3 "$t" 2>&1 | tail -25
done
kill $SRV
