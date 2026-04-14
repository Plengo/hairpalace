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

  # ── Service access URLs ──────────────────────────────────────────────────
  BASE_URL="${FRONTEND_URL:-http://localhost}"
  echo ""
  echo "╔══════════════════════════════════════════════════════════════════════╗"
  echo "║                  HAIR PALACE — SERVICE ACCESS MAP                  ║"
  echo "╠══════════════════════════════════════════════════════════════════════╣"
  echo "║  Storefront       ${BASE_URL}"
  echo "║  API Root         ${BASE_URL}/api/"
  echo "║  Swagger UI       ${BASE_URL}/api/docs"
  echo "║  ReDoc            ${BASE_URL}/api/redoc"
  echo "║  Health check     ${BASE_URL}/api/health"
  echo "╠══════════════════════════════════════════════════════════════════════╣"
  echo "║  ADMIN ACCESS (run on this server via docker exec):"
  echo "║"
  echo "║  Postgres (psql)"
  echo "║    docker compose exec postgres psql -U \$POSTGRES_USER -d \$POSTGRES_DB"
  echo "║"
  echo "║  Analytics DB"
  echo "║    docker compose exec analytics_db psql -U analytics -d hairpalace_analytics"
  echo "║"
  echo "║  Redis CLI"
  echo "║    docker compose exec redis redis-cli"
  echo "║"
  echo "║  Kafka / Redpanda (rpk)"
  echo "║    docker compose exec redpanda rpk cluster info"
  echo "║    docker compose exec redpanda rpk topic list"
  echo "║    docker compose exec redpanda rpk topic consume <topic> --offset start"
  echo "║"
  echo "║  Redpanda external broker (from dev machine via SSH tunnel):"
  echo "║    ssh -L 19092:localhost:19092 <user>@<server_ip>"
  echo "║    then: rpk topic list --brokers localhost:19092"
  echo "╚══════════════════════════════════════════════════════════════════════╝"
  echo ""
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

# ── Local access summary (SSH tunnel hints) ──────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║            HAIR PALACE — LOCAL TUNNEL ACCESS (optional)             ║"
echo "╠══════════════════════════════════════════════════════════════════════╣"
echo "║  Live site          https://hairpalace.co.za"
echo "║  Swagger UI         https://hairpalace.co.za/api/docs"
echo "║"
echo "║  To access internal services locally, open SSH tunnels:"
echo "║"
echo "║  Postgres (5432)"
echo "║    ssh -L 5432:localhost:5432 -i ${SSH_KEY} ${SSH_USER}@${SSH_HOST}"
echo "║    then: psql postgresql://\$POSTGRES_USER:\$POSTGRES_PASSWORD@localhost:5432/\$POSTGRES_DB"
echo "║"
echo "║  Redis (6379)"
echo "║    ssh -L 6379:localhost:6379 -i ${SSH_KEY} ${SSH_USER}@${SSH_HOST}"
echo "║    then: redis-cli -h 127.0.0.1"
echo "║"
echo "║  Kafka / Redpanda (19092 — external listener)"
echo "║    ssh -L 19092:localhost:19092 -i ${SSH_KEY} ${SSH_USER}@${SSH_HOST}"
echo "║    then: rpk topic list --brokers localhost:19092"
echo "║    or:   rpk topic consume <topic> --brokers localhost:19092 --offset start"
echo "║"
echo "║  Analytics DB (5433→5432)"
echo "║    ssh -L 5433:analytics_db:5432 -i ${SSH_KEY} ${SSH_USER}@${SSH_HOST}"
echo "║    then: psql postgresql://analytics:\$ANALYTICS_DB_PASSWORD@localhost:5433/hairpalace_analytics"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
