# Try it: Orama Lake on a laptop

One command brings up the whole stack in one container on your machine: lake, a workspace with its
own zetta, the agents, and a small open model that runs locally. **No account and no API key.** Your
documents stay on your machine.

> **Status: not available yet.** The installer is here and reads the [release manifest](../release/README.md),
> but the image it runs is not built or published yet. What is missing is listed at the
> [end of this page](#what-is-missing-today). Until then, use [Run it](run-it.md) on a Linux machine.

## Before you start

- macOS, Windows (with WSL 2) or Linux, with Docker running.
- At least 8 GB of memory for Docker, and 16 GB is better. 20 GB of free disk.
- No GPU is needed. If Docker can see one, the model uses it.

## Install

From a checkout of this repository:

```sh
install/install.sh try
```

Or on its own, which downloads the latest release manifest first:

```sh
curl -fsSL https://github.com/oramasearch/lake-platform/releases/latest/download/install.sh | bash -s try
```

When it is ready, it prints:

```text
orama-lake: Orama Lake is running at http://localhost:4900
https://localhost:4900/sign-in/first?token=...
```

Open the link to sign in as the first administrator. It works once. To print a new one:
`install/install.sh sign-in`.

## What to do first

1. Open **Ask** and ask a question about the sample documents in your first workspace.
2. Upload a folder of your own documents to the workspace's drive, and ask about those.
3. Ask the app builder for an app over them, and confirm the deploy.

## Stop, start, remove

| To | Run |
|---|---|
| See if it is running | `install/install.sh status` |
| Stop it (your data is kept) | `install/install.sh stop` |
| Start it again | `install/install.sh try` |
| Remove it, keeping the data | `install/install.sh uninstall` |
| Remove it and its data | `install/install.sh uninstall --delete-data` |

Settings: `LAKE_TRY_PORT` (default `4900`), `LAKE_TRY_CONTAINER` and `LAKE_TRY_VOLUME` (default
`orama-lake`), `LAKE_RELEASE_MANIFEST` (a path or an https URL of a `release.yaml`).

## What runs inside

The container runs the same stack as every other install, on a single-node Kubernetes:

| Inside the container | What it is |
|---|---|
| k0s | A single-node Kubernetes from the platform's k0s fork, controller and worker in one process |
| CloudNativePG | Postgres for lake's control plane |
| The operator | Reconciles the `Lake` and everything under it |
| lake | The workspace, with native sign-in, billing off |
| A workspace zetta | The engine for your first workspace, with the base model copied in |
| The agents | Ask, the app builder and the others, on agent-runtime |
| A local model server | An open-weights model on CPU (GPU if present), behind lake's model gateway |

Every image is in the container already, so the first start downloads nothing. All state is in one
Docker volume. The container is privileged because Kubernetes runs inside it; it listens only on
`127.0.0.1`.

## How the image is built

The image is part of a stack release ([`docs/release/README.md`](../release/README.md)):

1. The k0s fork's binary, at the version in `release.yaml`.
2. An image bundle made with `k0s airgap bundle-artifacts` from every image `release.yaml` names, plus
   its `dependencies`, placed in `/var/lib/k0s/images` so containerd imports it at start.
3. The CloudNativePG and operator charts, packaged.
4. A first-start script that starts k0s, installs the two charts, and applies one `Lake`: native
   sign-in, billing off, a local model, one replica, local-path storage.
5. A `lake-try` command that prints the sign-in link and the address.

## What is missing today

| Missing | Where it is tracked |
|---|---|
| The image itself, and a check that the fork runs in a container on Docker Desktop for macOS and Windows | https://github.com/oramasearch/k0s/issues/45 |
| A first administrator and a one-time sign-in link on first start; native sign-in and billing off by default | https://github.com/oramasearch/lake/issues/1307 |
| lake's model gateway calling a local model with no key, and a default model | https://github.com/oramasearch/lake/issues/1308 |
| The operator running the local model server for a `Lake` | https://github.com/oramasearch/orama-operator/issues/1187 |
| A model server on the OpenAI-compatible API | https://github.com/oramasearch/model-runtime/issues/3 |
| The agents checked on the local model | https://github.com/oramasearch/zetta-bridge/issues/2 |
| The base model image the operator copies into each workspace | https://github.com/oramasearch/base-agent-0.6b/issues/6 |
| Public images, so nothing needs a credential | https://github.com/oramasearch/orama-operator/issues/1186 |

The hardware numbers on this page are what the image must meet. They are replaced with measured
numbers when it exists.
