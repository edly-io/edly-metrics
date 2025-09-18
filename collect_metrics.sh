#!/usr/bin/env bash
set -euo pipefail

# Load .env if present
if [ -f .env ]; then
  # shellcheck disable=SC1091
  source .env
fi

python metrics_cli.py run release_success --date-from 2024-01-01 --date-to 2024-12-31 --output ./files/release_success.csv


