#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Hair Palace — Deploy Script
# ─────────────────────────────────────────────────────────────────────────────
# Usage (local or on server after scp):
#   bash scripts/deploy.sh
#
# What it does:
#   1. Sources .hairpalace  → exports all secrets to the shell
#   2. Runs envsubst        → resolves .env template → .env.live (real values)
#   3. Restarts containers  → docker compose picks up .env.live
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

SECRETS_FILE=".hairpalace"
ENV_TEMPLATE=".env"
ENV_LIVE=".env.live"

if [[ ! -f "$SECRETS_FILE" ]]; then
  echo "✗ $SECRETS_FILE not found — copy it to $(pwd)/$SECRETS_FILE and retry"
  exit 1
fi

echo "▶ Loading secrets from $SECRETS_FILE …"
set -a
# shellcheck source=../.hairpalace
source "$SECRETS_FILE"
set +a

echo "▶ Resolving $ENV_TEMPLATE → $ENV_LIVE …"
if ! command -v envsubst &>/dev/null; then
  echo "✗ envsubst not found — install gettext: apt install gettext-base"
  exit 1
fi
envsubst < "$ENV_TEMPLATE" > "$ENV_LIVE"

echo "▶ Pulling latest images …"
docker compose pull --quiet 2>/dev/null || true

echo "▶ Restarting containers …"
docker compose --env-file "$ENV_LIVE" up -d --force-recreate --remove-orphans

echo "✓ Done — all containers are up"
docker compose ps
