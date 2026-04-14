#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Hair Palace — Deploy Script
# ─────────────────────────────────────────────────────────────────────────────
# Run from your local machine:
#   bash scripts/deploy.sh
#
# What it does:
#   1. Sources .hairpalace locally  → loads secrets + SSH config
#   2. scp .hairpalace → server     → copies secrets file to server
#   3. ssh git pull                 → pulls latest code on server
#   4. ssh --local                  → resolves .env.live + restarts containers
#
# SSH config (set in .hairpalace):
#   SSH_HOST=156.155.250.65
#   SSH_USER=root
#   SSH_KEY=~/.ssh/hungu_rsa
#   REMOTE_DIR=/root/hairpalace
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

SECRETS_FILE=".hairpalace"
ENV_TEMPLATE=".env"
ENV_LIVE=".env.live"

# ── --local flag: runs entirely on the server ─────────────────────────────────
if [[ "${1:-}" == "--local" ]]; then
  echo "▶ [server] Loading secrets …"
  set -a; source "$SECRETS_FILE"; set +a

  if ! command -v envsubst &>/dev/null; then
    apt-get install -y gettext-base >/dev/null
  fi

  echo "▶ [server] Resolving $ENV_TEMPLATE → $ENV_LIVE …"
  envsubst < "$ENV_TEMPLATE" > "$ENV_LIVE"

  echo "▶ [server] Restarting containers …"
  docker compose --env-file "$ENV_LIVE" up -d --build --force-recreate --remove-orphans

  echo "✓ Deploy complete"
  docker compose ps
  exit 0
fi

# ── Local: orchestrate the full remote deploy ─────────────────────────────────
if [[ ! -f "$SECRETS_FILE" ]]; then
  echo "✗ $SECRETS_FILE not found in $(pwd)"
  exit 1
fi

echo "▶ Loading secrets from $SECRETS_FILE …"
set -a; source "$SECRETS_FILE"; set +a

SSH_OPTS="-i ${SSH_KEY} -o StrictHostKeyChecking=no -o BatchMode=yes"
REMOTE="${SSH_USER}@${SSH_HOST}"

echo "▶ Copying secrets to ${REMOTE}:${REMOTE_DIR} …"
scp $SSH_OPTS "$SECRETS_FILE" "${REMOTE}:${REMOTE_DIR}/$SECRETS_FILE"

echo "▶ Pulling latest code on server …"
ssh $SSH_OPTS "$REMOTE" "cd ${REMOTE_DIR} && git pull origin main"

echo "▶ Running remote deploy …"
ssh $SSH_OPTS "$REMOTE" "cd ${REMOTE_DIR} && bash scripts/deploy.sh --local"
