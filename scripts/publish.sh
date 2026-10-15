#!/usr/bin/env bash
# Publish the website: build with the pinned Hugo version and rsync `public/`
# to the university web server.
#
#   scripts/publish.sh --dry-run   # build, then show what rsync WOULD change
#   scripts/publish.sh             # build and publish
#   scripts/publish.sh --force     # skip the branch/clean-tree/up-to-date checks
#
# Settings come from publish.conf next to this repository's root
# (copy publish.conf.example; the file is git-ignored because it contains the
# server path).  Requires: git, hugo (extended, version in .hugo-version), rsync,
# and an SSH login to the web server that works without typing a password
# (ssh key or agent), otherwise rsync will prompt.
set -euo pipefail
cd "$(dirname "$0")/.."

CONF="publish.conf"
if [ ! -f "$CONF" ]; then
  echo "Missing $CONF - copy publish.conf.example to publish.conf and fill in RSYNC_TARGET." >&2
  exit 1
fi
# shellcheck source=publish.conf.example
source "$CONF"
: "${RSYNC_TARGET:?RSYNC_TARGET is not set in $CONF}"
BASE_URL="${BASE_URL:-https://resonantoptics.physics.otago.ac.nz/}"
DELETE_REMOTE="${DELETE_REMOTE:-yes}"

DRY=""
FORCE=0
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY="--dry-run" ;;
    --force) FORCE=1 ;;
    -h|--help) sed -n '2,15p' "$0"; exit 0 ;;
    *) echo "Unknown option: $arg" >&2; exit 2 ;;
  esac
done

# --- 1. Right Hugo? ---------------------------------------------------------
want="$(tr -d '[:space:]' < .hugo-version)"
have="$(hugo version 2>/dev/null | sed -E 's/^hugo v([0-9]+\.[0-9]+\.[0-9]+).*/\1/')"
if [ "$have" != "$want" ]; then
  echo "Hugo $have is installed but .hugo-version pins $want." >&2
  echo "Install that version (https://github.com/gohugoio/hugo/releases/tag/v$want) or change the pin deliberately." >&2
  exit 1
fi
if ! hugo version | grep -q '+extended'; then
  echo "The 'extended' build of Hugo is required (SCSS)." >&2
  exit 1
fi

# --- 2. Publishing what is on GitHub's main? --------------------------------
if [ "$FORCE" -eq 0 ]; then
  branch="$(git rev-parse --abbrev-ref HEAD)"
  if [ "$branch" != "main" ]; then
    echo "You are on branch '$branch'. Publish from 'main' only (git switch main), or use --force." >&2
    exit 1
  fi
  if [ -n "$(git status --porcelain)" ]; then
    echo "Working tree has uncommitted changes. Commit, stash or discard them first, or use --force." >&2
    git status --short >&2
    exit 1
  fi
  git fetch -q origin main
  if [ "$(git rev-parse HEAD)" != "$(git rev-parse origin/main)" ]; then
    echo "Local main is not identical to origin/main. 'git pull' (or push) first, or use --force." >&2
    exit 1
  fi
fi

# --- 3. Build ---------------------------------------------------------------
rm -rf public
HUGO_ENVIRONMENT=production hugo --gc --minify --baseURL "$BASE_URL"
pages="$(find public -name index.html | wc -l | tr -d ' ')"
echo "Built $pages pages from commit $(git rev-parse --short HEAD)."

# --- 4. Sync ----------------------------------------------------------------
opts=(-az --no-times --checksum --itemize-changes)
[ "$DELETE_REMOTE" = "yes" ] && opts+=(--delete)
[ -n "$DRY" ] && opts+=("$DRY")
echo "rsync ${opts[*]} public/ $RSYNC_TARGET"
rsync "${opts[@]}" public/ "$RSYNC_TARGET"

if [ -n "$DRY" ]; then
  echo "Dry run only - nothing was changed on the server."
else
  echo "Published $(git rev-parse --short HEAD) to $RSYNC_TARGET at $(date '+%Y-%m-%d %H:%M %Z')."
fi
