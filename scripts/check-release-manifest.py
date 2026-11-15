#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Check release.yaml against the commits this repository pins.

For every component with a `path`, the `commit` in the manifest must be the commit the repository
pins at that path: a direct submodule of this repository, or a submodule of one of its bridges. A
released manifest (`stack.status: released`) must also give every image a digest and every
component a version.

It reads git objects only; it never builds, fetches or changes anything. The bridges must be
initialized (`git submodule update --init modules/liquid-bridge modules/zetta-bridge`) so their
trees can be read.

    uv run --with pyyaml scripts/check-release-manifest.py [release.yaml]

Exits 0 when the manifest matches, 1 with one line per problem when it does not.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import sys

try:
    import yaml
except ImportError:  # pragma: no cover - the message is the point
    sys.exit("check-release-manifest: needs PyYAML (uv run --with pyyaml ...)")

# LAKE_PLATFORM_ROOT checks another checkout of this repository (one with its bridges initialized).
ROOT = pathlib.Path(os.environ.get("LAKE_PLATFORM_ROOT") or pathlib.Path(__file__).resolve().parent.parent)


def gitlink(repo: pathlib.Path, tree: str, path: str) -> str | None:
    """The commit a tree pins at `path`, or None when the path is not a submodule there."""
    result = subprocess.run(
        ["git", "-C", str(repo), "ls-tree", tree, "--", path],
        capture_output=True,
        text=True,
        check=False,
    )
    fields = result.stdout.split()
    if result.returncode != 0 or len(fields) < 3 or fields[1] != "commit":
        return None
    return fields[2]


def pinned_commit(path: str) -> str | None:
    """Resolve `modules/<x>` or `modules/<bridge>/modules/<x>` through the pins."""
    parts = path.split("/")
    if len(parts) == 2:
        return gitlink(ROOT, "HEAD", path)
    if len(parts) == 4 and parts[0] == "modules" and parts[2] == "modules":
        bridge_path = "/".join(parts[:2])
        bridge_commit = gitlink(ROOT, "HEAD", bridge_path)
        bridge_dir = ROOT / bridge_path
        if bridge_commit is None or not (bridge_dir / ".git").exists():
            return None
        return gitlink(bridge_dir, bridge_commit, "/".join(parts[2:]))
    return None


def main(argv: list[str]) -> int:
    manifest_path = pathlib.Path(argv[1]) if len(argv) > 1 else ROOT / "release.yaml"
    manifest = yaml.safe_load(manifest_path.read_text())
    problems: list[str] = []

    if manifest.get("schema") != 1:
        problems.append("schema: expected 1")
    stack = manifest.get("stack") or {}
    released = stack.get("status") == "released"

    names = set()
    for component in manifest.get("components") or []:
        name = component.get("name", "<unnamed>")
        if name in names:
            problems.append(f"{name}: listed twice")
        names.add(name)

        path = component.get("path")
        commit = component.get("commit")
        if path is None:
            if released:
                problems.append(f"{name}: not pinned by this repository")
        else:
            pinned = pinned_commit(path)
            if pinned is None:
                problems.append(f"{name}: cannot read the pin at {path} (is its bridge initialized?)")
            elif pinned != commit:
                problems.append(f"{name}: manifest says {commit}, the pin at {path} is {pinned}")

        if released and not component.get("version"):
            problems.append(f"{name}: a released stack needs a version for every component")
        for image in component.get("images") or []:
            if released and not image.get("digest"):
                problems.append(f"{name}: image {image.get('name')} has no digest")

    if released and not stack.get("published"):
        problems.append("stack: released but not published")

    for problem in problems:
        print(f"check-release-manifest: {problem}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
