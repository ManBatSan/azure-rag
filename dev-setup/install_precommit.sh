#!/usr/bin/env bash
set -euo pipefail

echo "Installing development dependencies..."
pip install --upgrade black isort ruff pre-commit

pip install --upgrade mypy

echo "Installing pre-commit hooks..."
pre-commit install

echo "✅ pre-commit setup complete!"
