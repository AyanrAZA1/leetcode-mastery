#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

echo "============================================================"
echo "🧠 LEETCODE MASTERY — MASTER PIPELINE V4"
echo "============================================================"

echo
echo "1️⃣ Inventory"
python3 10-Automation/scripts/inventory_v3.py

echo
echo "2️⃣ Classification"
python3 10-Automation/scripts/classify_v3.py

echo
echo "3️⃣ Revision state-preserving build"
python3 10-Automation/scripts/build_revision_v4.py

echo
echo "4️⃣ Dashboard"
python3 10-Automation/scripts/build_dashboard_v3.py

echo
echo "5️⃣ Validation"
python3 10-Automation/scripts/validate_v4.py

echo
echo "============================================================"
echo "✅ MASTER PIPELINE COMPLETED"
echo "============================================================"
