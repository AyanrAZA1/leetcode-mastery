#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

echo "=============================================="
echo "🚀 LEETCODE MASTERY MASTER PIPELINE"
echo "=============================================="

echo
echo "[1/6] Inventory V3"
python3 10-Automation/scripts/inventory_v3.py

echo
echo "[2/6] Classification V3"
python3 10-Automation/scripts/classify_v3.py

echo
echo "[3/6] Revision System"
if [ -f 10-Automation/scripts/build_revision_v4.py ]; then
    python3 10-Automation/scripts/build_revision_v4.py
elif [ -f 10-Automation/scripts/build_revision_v3.py ]; then
    python3 10-Automation/scripts/build_revision_v3.py
fi

echo
echo "[4/6] Dashboard"
if [ -f 10-Automation/scripts/build_dashboard_v3.py ]; then
    python3 10-Automation/scripts/build_dashboard_v3.py
fi

echo
echo "[5/6] Progress"
python3 scripts/update_progress_v5.py

echo
echo "[6/6] Validation"
if [ -f 10-Automation/scripts/validate_v4.py ]; then
    python3 10-Automation/scripts/validate_v4.py
fi

echo
echo "=============================================="
echo "✅ MASTER PIPELINE COMPLETE"
echo "=============================================="
