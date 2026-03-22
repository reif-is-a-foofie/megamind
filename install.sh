#!/bin/zsh
# megamind install
# Single-command setup: curl -fsSL https://raw.githubusercontent.com/.../install.sh | bash
set -e

MEGAMIND_HOME="${MEGAMIND_HOME:-$HOME/megamind}"
VENV="$MEGAMIND_HOME/.venv"

echo "==> megamind install"
echo "    home: $MEGAMIND_HOME"

# ── 1. Clone or update ────────────────────────────────────────────
if [[ -d "$MEGAMIND_HOME/.git" ]]; then
  echo "==> updating existing repo"
  git -C "$MEGAMIND_HOME" pull --ff-only
else
  echo "==> cloning"
  git clone https://github.com/reify/megamind "$MEGAMIND_HOME"
fi

cd "$MEGAMIND_HOME"

# ── 2. Python venv + deps ─────────────────────────────────────────
echo "==> python venv"
python3 -m venv "$VENV"
source "$VENV/bin/activate"

echo "==> installing python deps"
pip install --quiet --upgrade pip
# numpy<2 must be installed before sentence-transformers to avoid torch conflict
pip install --quiet "numpy<2"
pip install --quiet -r requirements.txt

# ── 3. bun (for apple-mcp) ────────────────────────────────────────
if ! command -v bun &>/dev/null && [[ ! -f "$HOME/.bun/bin/bun" ]]; then
  echo "==> installing bun"
  curl -fsSL https://bun.sh/install | bash
fi
export PATH="$HOME/.bun/bin:$PATH"

# ── 4. Node deps (gmail MCP) ──────────────────────────────────────
echo "==> warming npm cache for gmail MCP"
npx --yes @gongrzhe/server-gmail-autoauth-mcp --version 2>/dev/null || true

# ── 5. apple-mcp warm cache ───────────────────────────────────────
echo "==> warming bun cache for apple-mcp"
bunx --no-cache apple-mcp@latest &
BUN_PID=$!
sleep 4
kill $BUN_PID 2>/dev/null || true

# ── 6. Claude CLI check ───────────────────────────────────────────
if ! command -v claude &>/dev/null; then
  echo ""
  echo "  !! Claude CLI not found."
  echo "     Install: npm install -g @anthropic-ai/claude-code"
  echo "     Then re-run: $MEGAMIND_HOME/install.sh"
  echo ""
fi

# ── 7. bin symlink ───────────────────────────────────────────────
if [[ -d /usr/local/bin ]]; then
  ln -sf "$MEGAMIND_HOME/bin/megamind" /usr/local/bin/megamind 2>/dev/null || \
    sudo ln -sf "$MEGAMIND_HOME/bin/megamind" /usr/local/bin/megamind
  echo "==> symlinked: megamind -> /usr/local/bin/megamind"
fi

# ── 8. MCP sync — wire any MCPs needed by quadrants.yaml ─────────
echo "==> syncing MCPs"
source "$VENV/bin/activate"
python3 "$MEGAMIND_HOME/brain/mcp_sync.py"

# ── 9. Install background daemons ────────────────────────────────
echo "==> installing daemons (think, ingest, mcp-sync)"
"$MEGAMIND_HOME/bin/install-daemon"

# ── 10. Gmail auth ────────────────────────────────────────────────
mkdir -p "$HOME/.gmail-mcp"
# Bundle our OAuth app credentials — users just approve, never touch Google Cloud
cp "$MEGAMIND_HOME/config/gmail-oauth.keys.json" "$HOME/.gmail-mcp/gcp-oauth.keys.json"

if [[ ! -f "$HOME/.gmail-mcp/credentials.json" ]]; then
  echo ""
  echo "==> Gmail: opening browser for authorization..."
  npx -y @gongrzhe/server-gmail-autoauth-mcp auth
else
  echo "==> gmail auth: already configured"
fi

echo ""
echo "  ✦  megamind ready"
echo "     run: megamind"
echo ""
