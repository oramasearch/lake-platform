# scripts

Checks that read this repository and never change it.

| Script | Checks |
|---|---|
| [`check-release-manifest.py`](check-release-manifest.py) | Every `commit` in [`release.yaml`](../release.yaml) is the commit this repository pins; a released manifest also has a version for every component and a digest for every image. `uv run --with pyyaml scripts/check-release-manifest.py` |
