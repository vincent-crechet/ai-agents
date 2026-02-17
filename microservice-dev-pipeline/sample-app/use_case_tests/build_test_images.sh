#!/usr/bin/env bash
#
# Build Docker images for integration testing.
#
# Images are snapshots of the current code — rebuild after any code changes!
# Must be run from the repository root.
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Building test images from: $REPO_ROOT"
echo "========================================="

echo ""
echo "Building url-management:test..."
docker build -f "$REPO_ROOT/services/url-management/Dockerfile" -t url-management:test "$REPO_ROOT"

echo ""
echo "Building analytics:test..."
docker build -f "$REPO_ROOT/services/analytics/Dockerfile" -t analytics:test "$REPO_ROOT"

echo ""
echo "========================================="
echo "All images built successfully."
echo ""
echo "WARNING: These images are snapshots of your current code."
echo "         Re-run this script after any code changes!"
