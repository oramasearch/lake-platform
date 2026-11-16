# Roadmap

What we are working on next, in the open. It is changed by pull request, and a large item starts as
an RFC ([`GOVERNANCE.md`](GOVERNANCE.md#rfcs)). Nothing here has a date: an item is done when it works,
and the release notes say when that was.

Each item says what is true today, so the list doubles as the honest account of what is not there yet.

## Now: installable by anyone, on their own hardware

| Item | Today |
|---|---|
| **Try it on a laptop**: one command, the whole stack in one container, no account and no API key ([guide](docs/install/try-it.md)) | The installer and the design exist; the all-in-one image does not yet |
| **A local model by default**: the quickstart and the agents run on an open-weights model on your own machine; a hosted model is optional configuration | The agents call a hosted model through lake's model gateway |
| **Native sign-in as the default** for a self-hosted Lake, with a first administrator on first start | lake has its own sign-in; it is not yet the default, and there is no first-run administrator |
| **Public, signed images** with SBOMs, built from release tags, and operator defaults that point at them | Every image is private |
| **One stack version** across the components, in [`release.yaml`](release.yaml) | A draft that matches this repository's pins |
| **Run it** on one machine with k0s ([guide](docs/install/run-it.md)), proven end to end on a clean host | Written, not yet run end to end |
| **Scale it** on any Kubernetes ([guide](docs/install/scale-it.md)), proven on more than one provider and on a plain upstream cluster | Proven on one managed provider and on k0s |
| **Air-gapped**: one signed bundle ([design](docs/install/air-gapped.md)) | A manual procedure; the bundle is not built yet |
| **A docs site**: quickstarts, architecture, and a reference generated from the code (OpenAPI, CLI, resources) | Docs live in each component's `docs/` |

## Build and review

- Checks that run on every push, and required checks before a change can land, run by the stack's own
  build system.
- Build and test results shown in review.
- Test runners beyond CMake.
- liquid at full parity on Linux: its build wrapper's file-system layer does not work there yet.
- A preview for every change, torn down when the change lands.

## Data

- A Postgres-compatible wire protocol, so outside BI tools can connect to zetta. Today dashboards are
  built as apps on the stack.
- Open table formats, and tiered storage.
- Clustered pub/sub.
- More connectors to the databases you already run.
- Backups and resizing for managed databases.
- Vector search in the engine itself; today it comes through OramaCore.

## AI

- Fine-tuning a language model on your own data, in your own environment. Training machine-learning
  models on your data works today.
- Agents that can change the agents they created.
- More app runtimes.
- Drift monitoring for served models.

## Platform

- The operator on more Kubernetes distributions and clouds.
- More package formats in the registry.
- Notebooks in lake (zetta's own interface has them today).
- A first release of liquify, the IDE.
- Packages of liquid for the common package managers, built by liquid itself.

## Community

- The community space, open from the first public preview.
- A good-first-issue set in every repository, kept fresh.
- Monthly community calls, recorded.
