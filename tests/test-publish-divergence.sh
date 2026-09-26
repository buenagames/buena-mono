#!/usr/bin/env bash
# Tests for scripts/check-public-divergence.sh, the guard publish-public.sh runs
# before its --delete rsync. Everything happens in a throwaway directory: a bare
# repo stands in for github.com/buenagames/buena-mono and a clone of it for the
# public clone, so nothing here can reach GitHub.
#
#   bash tests/test-publish-divergence.sh [workdir]
#
# Every foreign commit below is made as buena@buenalabs.io on purpose: that is
# the case the committer-based guard it replaced could not see.
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
GUARD="$HERE/scripts/check-public-divergence.sh"
W="${1:-$(mktemp -d)}"
rm -rf "$W/origin.git" "$W/pub" "$W/other" "$W/tree"
mkdir -p "$W"
export GIT_AUTHOR_NAME=Buena GIT_AUTHOR_EMAIL=buena@buenalabs.io
export GIT_COMMITTER_NAME=Buena GIT_COMMITTER_EMAIL=buena@buenalabs.io
unset ALLOW_CLOBBER

pass=0; failures=0
ok()   { echo "PASS  $1"; pass=$((pass + 1)); }
bad()  { echo "FAIL  $1"; failures=$((failures + 1)); }

git init -q --bare -b main "$W/origin.git"
git clone -q "$W/origin.git" "$W/pub" 2>/dev/null
case "$(git -C "$W/pub" remote get-url origin)" in
  "$W/origin.git") ;; *) echo "origin is not the local bare repo; refusing to run" >&2; exit 1 ;;
esac
# A second clone plays GitHub: the web UI, a PR merge, someone else's laptop.
git clone -q "$W/origin.git" "$W/other" 2>/dev/null

# The tree the canonical repo would publish.
mkdir -p "$W/tree"
printf 'fonts\n' > "$W/tree/README.md"
printf 'OFL\n'   > "$W/tree/OFL.txt"

# What publish-public.sh does after the guard, minus the build.
publish() {
  git -C "$W/pub" fetch -q origin
  git -C "$W/pub" reset -q --hard origin/main 2>/dev/null || true
  rsync -a --delete --exclude=.git "$W/tree"/ "$W/pub"/
  git -C "$W/pub" add -A
  git -C "$W/pub" diff --cached --quiet || git -C "$W/pub" commit -q -m "Buena Mono $1"
  git -C "$W/pub" push -q origin HEAD:main
  bash "$GUARD" record "$W/pub" >/dev/null
}
guard() {
  git -C "$W/pub" fetch -q origin
  bash "$GUARD" check "$W/pub" "$W/tree" >"$W/out" 2>&1
}
foreign() {  # foreign <file> <content> <subject>: a direct commit in the public repo, as Buena
  git -C "$W/other" pull -q --ff-only origin main
  printf '%s\n' "$2" > "$W/other/$1"
  git -C "$W/other" add "$1"
  git -C "$W/other" commit -q -m "$3"
  git -C "$W/other" push -q origin HEAD:main
}
expect() {  # expect <name> <exit> <grep-pattern>...
  local name="$1" want="$2" got=0; shift 2
  guard || got=$?
  [ "$got" = "$want" ] || { bad "$name: exit $got, want $want"; sed 's/^/      /' "$W/out"; return; }
  for pat in "$@"; do
    grep -q -- "$pat" "$W/out" || { bad "$name: output lacks '$pat'"; sed 's/^/      /' "$W/out"; return; }
  done
  ok "$name"
  sed 's/^/      /' "$W/out"
}

# 1. publish, then publish again: nothing in between, nothing to refuse.
publish 1.0
expect "publish after publish is clean" 0 "nothing committed on origin/main since; clean"

# 2. a direct commit in the public repo as Buena: refused, file and commit named.
foreign package.json '{"name":"buena-mono"}' "feat: npm package"
c2="$(git -C "$W/other" rev-parse --short HEAD)"
expect "direct Buena commit is refused" 1 "package.json would be deleted" "$c2" "feat: npm package"

# 4. ALLOW_CLOBBER=1 proceeds and says what it discards.
export ALLOW_CLOBBER=1
expect "ALLOW_CLOBBER=1 proceeds and names the loss" 0 "ALLOW_CLOBBER=1 — discarding" "package.json would be deleted"
unset ALLOW_CLOBBER
publish 1.1   # the clobbering publish; the marker moves past the foreign commit
expect "clean again after the clobbering publish" 0 "clean"

# 3. the same via a merge commit, as GitHub writes one for a PR.
git -C "$W/other" pull -q --ff-only origin main
git -C "$W/other" checkout -q -b feat/agents
printf 'agents\n' > "$W/other/AGENTS.md"
git -C "$W/other" add AGENTS.md
git -C "$W/other" commit -q -m "docs(agents): add AGENTS.md"
git -C "$W/other" checkout -q main
git -C "$W/other" merge -q --no-ff -m "Merge pull request #2 from buenagames/feat/agents" feat/agents
git -C "$W/other" push -q origin HEAD:main
m3="$(git -C "$W/other" rev-parse --short HEAD)"
expect "PR merge commit is refused" 1 "AGENTS.md would be deleted" "$m3" "Merge pull request #2"

# A foreign change already ported to the canonical tree loses nothing.
printf 'agents\n' > "$W/tree/AGENTS.md"
expect "already-ported foreign change is not refused" 0 "AGENTS.md (already matches this tree)"
publish 1.2

# A foreign edit of a published file is "overwritten", a foreign delete "re-added".
foreign OFL.txt 'OFL edited on GitHub' "Update OFL.txt"
expect "foreign edit of a published file is refused" 1 "OFL.txt would be overwritten"
git -C "$W/other" rm -q README.md; git -C "$W/other" commit -q -m "Delete README.md"; git -C "$W/other" push -q origin HEAD:main
expect "foreign delete is refused" 1 "README.md would be re-added"
ALLOW_CLOBBER=1 publish 1.3

# 5. first run with no marker: fall back to the newest publish-shaped commit.
git -C "$W/pub" update-ref -d refs/publish/last
expect "no marker, nothing since the last publish: clean" 0 "WARNING: no refs/publish/last" "Buena Mono 1.3" "clean"
foreign index.css '@font-face{}' "feat: npm css"
expect "no marker, Buena commit after it: still refused" 1 "Buena Mono 1.3" "index.css would be deleted"
# ...and after the next publish the marker is real again.
ALLOW_CLOBBER=1 publish 1.4
if git -C "$W/pub" rev-parse -q --verify refs/publish/last >/dev/null; then ok "publish records the marker"; else bad "publish records the marker"; fi
expect "marker restored: clean" 0 "last publish: .*Buena Mono 1.4" "clean"

# 5b. no marker and nothing that looks like a publish: refuse with the bootstrap.
rm -rf "$W/bare2.git" "$W/pub2"
git init -q --bare -b main "$W/bare2.git"
git clone -q "$W/bare2.git" "$W/pub2" 2>/dev/null
printf 'x\n' > "$W/pub2/x"; git -C "$W/pub2" add x; git -C "$W/pub2" commit -q -m "Initial commit"; git -C "$W/pub2" push -q origin HEAD:main
got=0; bash "$GUARD" check "$W/pub2" "$W/tree" >"$W/out" 2>&1 || got=$?
if [ "$got" = 1 ] && grep -q "update-ref refs/publish/last <commit>" "$W/out"; then ok "no marker, no publish-shaped commit: refuses with bootstrap"; sed 's/^/      /' "$W/out"
else bad "no marker, no publish-shaped commit: exit $got"; sed 's/^/      /' "$W/out"; fi

# A marker outside origin/main's history (main was force-pushed) is refused.
git -C "$W/other" pull -q --ff-only origin main
git -C "$W/other" reset -q --hard HEAD~1
printf 'rewritten\n' > "$W/other/OFL.txt"; git -C "$W/other" commit -qam "Buena Mono 9.9"
git -C "$W/other" push -q -f origin HEAD:main
expect "rewritten public history is refused" 1 "is not in origin/main's history"

echo ""
echo "$pass passed, $failures failed  ($W)"
[ "$failures" -eq 0 ]
