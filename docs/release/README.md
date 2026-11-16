# The release manifest

[`release.yaml`](../../release.yaml) at the root of this repository is **one version of the whole
stack**. It pins every component (its source commit, its version, and the images, charts and binaries
built from it), so a user installs "Orama Lake 0.1" and never has to work out which zetta goes with
which lake.

**State:** v0.1.1, a patch of v0.1.0, the first release. Every component is pinned at its released
version, and `scripts/check-release-manifest.py` passes. The image `digest` fields are still empty,
and `published` stays `false` until the images are signed.

## Who reads it

| Reader | What it takes from the manifest |
|---|---|
| The installer ([`install/install.sh`](../../install/install.sh)) | The stack version, the registry, and the images it pulls |
| The Helm path ([`docs/install/scale-it.md`](../install/scale-it.md)) | The operator chart's version and the lake image |
| The air-gapped bundle ([`docs/install/air-gapped.md`](../install/air-gapped.md)) | Every image and chart, with its digest, so the bundle holds exactly these |
| The operator's built-in defaults | The default image of every workload it runs. They are generated from this file, so they cannot drift from the release |
| A hosted Lake | The same file, so the hosted service runs the same release as a self-hosted one |

## The fields

```yaml
schema: 1                      # the format of this file
stack:
  name: Orama Lake
  version: 0.9.0               # the stack version: one number for the whole platform
  status: candidate            # draft, candidate or released
  published: false             # true once every image is public and signed
registry: docker.io/oramasearch   # every image name is relative to it; a mirror overrides it here
components:
  - name: lake
    repository: https://github.com/oramasearch/lake
    path: modules/liquid-bridge/modules/lake   # where this repository pins it
    commit: <the pinned commit>
    version: v0.8.1            # the component's own release tag, or null when it has none
    images:  [{name: lake, tag: v0.8.1, digest: sha256:...}]
    charts:  [{name: ..., version: ..., oci: ..., digest: ...}]
    artifacts: [{kind: binary, name: ..., platforms: [...]}]
dependencies:                  # open-source charts and images the stack runs but does not build
  charts: [...]
  images: [...]
```

- **The stack has one version**, and each component keeps its own. A developer who takes only liquid
  or only zetta uses the component's version; someone installing Orama Lake uses the stack's.
- **`commit` is the pin.** It is the commit this repository pins at `path`, and nothing else.
  [`scripts/check-release-manifest.py`](../../scripts/check-release-manifest.py) fails when they
  differ.
- **An image is named by its digest at release.** The tag is for people; the digest is what is
  installed. A released manifest has a digest for every image.
- **`dependencies`** are the open-source images the stack runs and pulls from their own registries.
  They are listed so the air-gapped bundle can carry them, each pinned by digest at release.

## Check it

```sh
git submodule update --init modules/liquid-bridge modules/zetta-bridge
uv run --with pyyaml scripts/check-release-manifest.py
```

It reads git objects only. It never builds or fetches anything.

## Cutting a stack release

A stack release is cut after each component it pins has been released on its own:

1. **Every component is released.** Each one has a version tag, release notes, and an image built from
   that tag, signed, with an SBOM.
2. **The pins move.** Each bridge pins its components at their tags, and this repository pins the
   bridges. Pins that depend on each other move together.
3. **The manifest is written** from the pins: every `commit`, `version`, image tag and digest. The
   check passes.
4. **The upgrade is tested**, from the previous stack version to this one, as well as a fresh install.
5. **The release notes** go in `docs/releases/<version>.md`: the component versions in it, what changed,
   what is known not to work, and how to upgrade from the version before.
6. **The tag** `v<version>` is put on the commit that holds the manifest, and the release is published
   from the notes, with the installer and the air-gapped bundle attached.

## What is not decided yet

- **Image signatures and digests.** The images are public on Docker Hub; their digests go in the
  manifest, and `published` becomes `true`, once they are signed.

## What v0.1.1 still lacks

- `lake-mcp-runner` is not pinned by this repository.
- The `k0s` fork is pinned by commit; it has no release tag of its own.
- The one-command `try` image (`lake-try`) is not built yet; *Try it* runs on a local k0s meanwhile.
