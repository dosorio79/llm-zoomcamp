#!/usr/bin/env bash

set -euo pipefail

ENV_FILE=".env"

if [ ! -f "$ENV_FILE" ]; then
  echo "Missing $ENV_FILE"
  exit 1
fi

set -a
source "$ENV_FILE"
set +a

base64_encode() {
  printf "%s" "$1" | base64 -w 0
}

cat > "$ENV_FILE" <<EOF
# Raw keys
GEMINI_API_KEY=${GEMINI_API_KEY}
OPENAI_API_KEY=${OPENAI_API_KEY}
TAVILY_API_KEY=${TAVILY_API_KEY}

# Kestra-compatible base64 secrets
SECRET_GEMINI_API_KEY=$(base64_encode "$GEMINI_API_KEY")
SECRET_OPENAI_API_KEY=$(base64_encode "$OPENAI_API_KEY")
SECRET_TAVILY_API_KEY=$(base64_encode "$TAVILY_API_KEY")
EOF

echo "Updated $ENV_FILE with encoded Kestra secrets."