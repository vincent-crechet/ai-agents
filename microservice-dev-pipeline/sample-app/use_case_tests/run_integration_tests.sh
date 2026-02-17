#!/usr/bin/env bash
#
# Run use case tests against real containerized services.
#
# This script:
# 1. Builds Docker images
# 2. Runs pytest with --integration flag
# 3. Cleans up containers on exit
#
# Must be run from the repository root.
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"

echo "Step 1: Building test images..."
bash "$SCRIPT_DIR/build_test_images.sh"

echo ""
echo "Step 2: Running integration tests..."
PYTHONPATH="$REPO_ROOT" python3 -m pytest use_case_tests/ --integration -v "$@"

echo ""
echo "Integration tests complete."
