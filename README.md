# Orama Lake

**The sovereign AI stack.** Orama Lake is an AI platform: an AI easy button with batteries included.
Everything you need to design, train, and ship real AI that learned on your own data, on your own
hardware.

It makes it easier for your whole team to create and ship apps, agents and AI. You use AI to create
and ship AI.

This repository is the entry point. It holds no product source. It pins every component of the
platform at versions that work together, and it is where the installers, the release manifest and the
guides live.

> **Status: pre-release.** This repository and the components it pins are private while the release is
> prepared. The install paths below are being built, and nothing here is published yet.

## What's in the platform

Each component is its own repository, pinned here under `modules/`.

| Component | What it is | Path |
|---|---|---|
| **lake** | Where you work: the workspace where you build, train and ship AI on your own data, with agents, apps, repositories, search, file storage, sign-in, secrets and a container registry. Everything it can do is one API, served as REST, OpenAPI and MCP. | [`modules/lake`](modules/lake) |
| **zetta** | The engine underneath, in C++26. A cluster of equal peers with no leader. It stores and queries your data, searches it, trains machine-learning models on it, and explains their predictions. | [`modules/zetta`](modules/zetta) |
| **liquid** | Differential source control, builds, packages and deploys in one program. Every write is captured and signed. It imports from Git and exports back to it. | [`modules/liquid`](modules/liquid) |
| **orama-operator** | Runs the whole platform on your own Kubernetes clusters. You describe what you want, and it makes the cluster match. | [`modules/orama-operator`](modules/orama-operator) |
| **zetta-tunnel** | Tunnels, a private mesh with mutual TLS, and ingress. | [`modules/zetta-tunnel`](modules/zetta-tunnel) |
| **liquify** | The IDE. Early, with no release yet. | [`modules/liquify`](modules/liquify) |

### Sidecars and runtimes

| Component | What it is | Path |
|---|---|---|
| lake-sqlite, lake-duckdb, lake-polars | lake's data sidecars | [`modules/lake-sqlite`](modules/lake-sqlite) · [`modules/lake-duckdb`](modules/lake-duckdb) · [`modules/lake-polars`](modules/lake-polars) |
| lake-builder | Builds the images lake deploys | [`modules/lake-builder`](modules/lake-builder) |
| app-runtime | What the apps you build run on | [`modules/app-runtime`](modules/app-runtime) |
| methodology-runtime | What machine-learning methodologies run on | [`modules/methodology-runtime`](modules/methodology-runtime) |
| k0s | The small Kubernetes distribution the single-machine and air-gapped installs use. A fork, under its upstream Apache-2.0 license | [`modules/k0s`](modules/k0s) |

### Agents and models

| Component | What it is | Path |
|---|---|---|
| agent-runtime | What every agent runs on, including the ones you create | [`modules/agent-runtime`](modules/agent-runtime) |
| agent-creator | Builds agents from a description | [`modules/agent-creator`](modules/agent-creator) |
| agent-application | Builds apps from a description and deploys them when you confirm | [`modules/agent-application`](modules/agent-application) |
| agent-ask-orama | The assistant you ask questions | [`modules/agent-ask-orama`](modules/agent-ask-orama) |
| agent-project | Builds and operates solutions and pipelines | [`modules/agent-project`](modules/agent-project) |
| agent-autosuggest | Proposes what is worth building from your data | [`modules/agent-autosuggest`](modules/agent-autosuggest) |
| agent-experiments | Designs and runs experiments | [`modules/agent-experiments`](modules/agent-experiments) |
| agent-eval-generator | Writes the test cases agents are measured against | [`modules/agent-eval-generator`](modules/agent-eval-generator) |
| agent-project-corpus, agent-autosuggest-corpus | The agents' training corpora | [`modules/agent-project-corpus`](modules/agent-project-corpus) · [`modules/agent-autosuggest-corpus`](modules/agent-autosuggest-corpus) |
| base-agent-0.6b | The base model the agents run on | [`modules/base-agent-0.6b`](modules/base-agent-0.6b) |
| model-runtime | Training and inference for the models | [`modules/model-runtime`](modules/model-runtime) |

The C++ libraries the engine vendors (the CRDT library, the full-text search library, the networking
libraries) are submodules of the components that use them, so they arrive with a recursive clone.

## Get the source

```sh
git clone --recurse-submodules https://github.com/oramasearch/lake-platform.git
```

To take one component only:

```sh
git clone https://github.com/oramasearch/lake-platform.git
cd lake-platform
git submodule update --init modules/lake
```

Each component's own README says how to build and test it.

## Install paths

These are the ways the platform will be installed. They are being built, and this section gets the
commands as each one works from a clean machine.

1. **Try it** on a laptop, with one command.
2. **Run it** on one machine or a small cluster, with k0s and the operator.
3. **Scale it** on any Kubernetes cluster, with the operator's Helm chart.
4. **Air-gapped**, from one signed bundle, with nothing fetched from outside.

## How the pins work

- Every component is pinned at a commit on its release branch (`main`; `liquid` for the k0s fork).
  A component's `main` is its last release.
- The pins move together. A commit in this repository is one set of component versions that work
  with each other.
- To see what is pinned: `git submodule status`.

## License

Orama Lake is being released under the MIT license. Forks of third-party code keep their upstream
licenses, and model weights carry their base model's license.
