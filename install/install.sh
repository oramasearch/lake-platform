#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
#
# The Orama Lake installer.
#
#   install.sh try          Try it: the whole stack in one container on this machine (Docker).
#   install.sh status       Is the Try-it container running, and where does it answer.
#   install.sh sign-in      Print the sign-in link for the first administrator again.
#   install.sh stop         Stop the Try-it container. Your data stays in its volume.
#   install.sh uninstall    Remove the Try-it container. Add --delete-data to remove its volume too.
#   install.sh server       Run it: Kubernetes (k0s), the operator and a Lake on this Linux machine.
#
# Every version comes from one release manifest (release.yaml). The installer reads it from this
# checkout, or from LAKE_RELEASE_MANIFEST (a path or an https URL) when it runs on its own.
#
# Try it needs no account and no API key: the model runs inside the container, on this machine.

set -euo pipefail

readonly default_manifest_url="https://github.com/oramasearch/lake-platform/releases/latest/download/release.yaml"
readonly container_name="${LAKE_TRY_CONTAINER:-orama-lake}"
readonly volume_name="${LAKE_TRY_VOLUME:-orama-lake}"
readonly host_port="${LAKE_TRY_PORT:-4900}"
readonly wait_seconds="${LAKE_TRY_WAIT_SECONDS:-900}"
readonly min_memory_bytes=$((8 * 1024 * 1024 * 1024))

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]:-$0}")" && pwd)"
readonly script_dir

manifest_file=""

say() { printf 'orama-lake: %s\n' "$*"; }
fail() {
  printf 'orama-lake: %s\n' "$*" >&2
  exit 1
}
require_command() { command -v "$1" >/dev/null 2>&1 || fail "required command not found: $1"; }

# --- the release manifest --------------------------------------------------------------------------

load_manifest() {
  local source="${LAKE_RELEASE_MANIFEST:-}"

  if [ -z "$source" ] && [ -f "$script_dir/../release.yaml" ]; then
    source="$script_dir/../release.yaml"
  fi
  source="${source:-$default_manifest_url}"

  case "$source" in
    https://*)
      require_command curl
      manifest_file="$(mktemp)"
      trap 'rm -f "$manifest_file"' EXIT
      curl -fsSL "$source" -o "$manifest_file" || fail "could not download the release manifest from $source"
      ;;
    *)
      [ -f "$source" ] || fail "release manifest not found: $source"
      manifest_file="$source"
      ;;
  esac
}

# The value of a top-level scalar, e.g. `registry`.
manifest_scalar() {
  sed -n "s/^$1:[[:space:]]*\\([^#[:space:]]*\\).*/\\1/p" "$manifest_file" | head -n 1
}

# The stack version (stack.version).
manifest_stack_version() {
  awk '/^stack:/ {in_stack = 1; next} /^[^[:space:]#]/ {in_stack = 0}
       in_stack && $1 == "version:" {print $2; exit}' "$manifest_file"
}

# A full image reference for a flow-style entry `{name: <name>, tag: <tag>, digest: <digest>}`.
manifest_image() {
  local name="$1"
  local registry
  local line
  local tag
  local digest

  registry="$(manifest_scalar registry)"
  line="$(grep -E "\\{name: ${name}, tag: " "$manifest_file" | head -n 1)" ||
    fail "the release manifest names no image $name"
  tag="$(sed -n 's/.*tag: \([^,}]*\).*/\1/p' <<<"$line")"
  digest="$(sed -n 's/.*digest: \([^,}]*\).*/\1/p' <<<"$line")"

  if [ -n "$digest" ] && [ "$digest" != null ]; then
    printf '%s/%s:%s@%s\n' "$registry" "$name" "$tag" "$digest"
  else
    printf '%s/%s:%s\n' "$registry" "$name" "$tag"
  fi
}

manifest_published() {
  awk '/^stack:/ {in_stack = 1; next} /^[^[:space:]#]/ {in_stack = 0}
       in_stack && $1 == "published:" {print $2; exit}' "$manifest_file"
}

# --- Try it ----------------------------------------------------------------------------------------

check_docker() {
  require_command docker
  require_command curl
  docker info >/dev/null 2>&1 || fail "Docker is installed but not running. Start Docker and run this again."

  local memory
  memory="$(docker info --format '{{.MemTotal}}' 2>/dev/null || echo 0)"
  if [ "${memory:-0}" -lt "$min_memory_bytes" ]; then
    say "Docker has less than 8 GB of memory. Orama Lake may start slowly or not at all."
    say "Give Docker more memory in its settings if you can."
  fi
}

container_exists() { docker container inspect "$container_name" >/dev/null 2>&1; }
container_running() {
  [ "$(docker container inspect -f '{{.State.Running}}' "$container_name" 2>/dev/null || echo false)" = true ]
}

wait_until_ready() {
  local deadline=$((SECONDS + wait_seconds))
  local url="http://127.0.0.1:${host_port}/readyz"

  say "waiting for Orama Lake to start (the first start unpacks every image)"
  until curl -fsS -o /dev/null "$url" 2>/dev/null; do
    container_running || fail "the container stopped. Its log: docker logs $container_name"
    [ "$SECONDS" -lt "$deadline" ] || fail "Orama Lake did not answer at $url. Its log: docker logs $container_name"
    sleep 5
  done
}

print_sign_in() {
  say "Orama Lake is running at http://localhost:${host_port}"
  # The image creates the first administrator on its first start and keeps a one-time sign-in link.
  docker exec "$container_name" lake-try sign-in-link ||
    say "no sign-in link yet: run 'install.sh sign-in' in a moment"
}

try_it() {
  local image

  load_manifest
  check_docker
  image="$(manifest_image lake-try)"

  if container_exists; then
    if ! container_running; then
      say "starting the existing Orama Lake container"
      docker start "$container_name" >/dev/null
    fi
    wait_until_ready
    print_sign_in
    return
  fi

  if [ "$(manifest_published)" != true ]; then
    say "release $(manifest_stack_version) of Orama Lake is not published yet; trying anyway"
  fi
  say "pulling $image"
  docker pull "$image" >/dev/null ||
    fail "could not pull $image. If this release is not published yet, see docs/install/try-it.md"

  # k0s runs inside the container, so it needs a privileged container with the host's cgroups.
  # Everything it stores is in one volume, so stop and start keep your data.
  docker run --detach \
    --name "$container_name" \
    --hostname "$container_name" \
    --privileged \
    --cgroupns=host \
    --tmpfs /run \
    --tmpfs /var/run \
    --volume "$volume_name:/var/lib/k0s" \
    --publish "127.0.0.1:${host_port}:4900" \
    "$image" >/dev/null

  wait_until_ready
  print_sign_in
}

status() {
  require_command docker
  if container_running; then
    say "running at http://localhost:${host_port}"
  elif container_exists; then
    say "stopped. Start it again with: install.sh try"
  else
    say "not installed"
  fi
}

stop() {
  require_command docker
  container_exists || fail "not installed"
  docker stop "$container_name" >/dev/null
  say "stopped. Your data is kept in the volume $volume_name"
}

uninstall() {
  require_command docker
  if container_exists; then
    docker rm --force "$container_name" >/dev/null
    say "removed the container"
  fi
  if [ "${1:-}" = --delete-data ]; then
    docker volume rm "$volume_name" >/dev/null 2>&1 && say "removed the volume $volume_name"
  else
    say "kept the volume $volume_name; add --delete-data to remove it"
  fi
}

# --- Run it on a server ----------------------------------------------------------------------------

server() {
  local k0s_dir="$script_dir/../modules/liquid-bridge/modules/k0s"
  local chart_dir="$script_dir/../modules/orama-operator/chart"

  [ "$(uname -s)" = Linux ] || fail "the server path runs on Linux. On a laptop, use: install.sh try"
  [ -x "$k0s_dir/hack/lake-on-k0s/install.sh" ] && [ -f "$chart_dir/Chart.yaml" ] ||
    fail "the server path runs from a checkout of lake-platform with its modules initialized (docs/install/run-it.md)"

  OPERATOR_CHART="$chart_dir" "$k0s_dir/hack/lake-on-k0s/install.sh"
}

usage() {
  sed -n '3,14p' "$0" | sed 's/^# \{0,1\}//'
  exit "${1:-0}"
}

main() {
  case "${1:-}" in
    try) try_it ;;
    status) status ;;
    sign-in)
      require_command docker
      print_sign_in
      ;;
    stop) stop ;;
    uninstall) uninstall "${2:-}" ;;
    server) server ;;
    -h | --help | help) usage 0 ;;
    "") try_it ;;
    *) usage 1 ;;
  esac
}

main "$@"
