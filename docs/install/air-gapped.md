# Air-gapped: one signed bundle, nothing fetched from outside

For networks with no way out: everything Orama Lake runs, in one file you check and carry in. The
install inside is [Run it](run-it.md) or [Scale it](scale-it.md), with every image, chart, binary and
model coming from the bundle.

> **Status: a design.** The pieces exist today as a manual procedure (the operator's
> [air-gapped variant](https://github.com/oramasearch/orama-operator/blob/main/docs/install/k0s.md#air-gapped-variant),
> made with the k0s fork's `k0s airgap bundle-artifacts`). The packaged bundle described here is built
> with a stack release and does not exist yet.

## What the bundle holds

`orama-lake-bundle-<version>.tar`, one per architecture (`amd64`, `arm64`):

| Path in the bundle | What it is |
|---|---|
| `release.yaml` | The [release manifest](../release/README.md) the bundle was made from. Every other file is listed in it, by digest |
| `images/images.tar` | An OCI image archive of every image in `release.yaml` and its `dependencies`, plus every image the k0s fork declares (`k0s airgap list-images --all`) |
| `charts/` | The operator chart and every chart in `dependencies`, packaged (`.tgz`) and unpacked |
| `bin/` | The k0s fork's binary, `liquid`, the installer, and the k0s fork's `lake-on-k0s` script |
| `models/` | The model weights as images inside `images.tar`, listed here with their licenses |
| `SBOM/` | An SBOM for every image and binary |
| `LICENSES/` | The license of every component and dependency, and the third-party notices |
| `checksums.txt` | A SHA-256 of every file in the bundle |

Beside it, published with the release: `orama-lake-bundle-<version>.tar.sha256` and a signature over
the checksum, as a Sigstore bundle.

## Check it before it goes in

On a connected machine, then again inside:

```sh
sha256sum -c orama-lake-bundle-<version>.tar.sha256
cosign verify-blob --bundle orama-lake-bundle-<version>.tar.sigstore.json \
  orama-lake-bundle-<version>.tar
tar -xf orama-lake-bundle-<version>.tar && (cd orama-lake-bundle-<version> && sha256sum -c checksums.txt)
```

`liquid verify` checks the same signature with liquid's own transparency log.

## Install inside

**One machine, or a small cluster, with k0s.** Place the image archive where k0s's containerd imports
it before k0s starts, then install as on a connected host, with the charts from the bundle:

```sh
sudo install -d -m 0755 /var/lib/k0s/images
sudo cp images/images.tar /var/lib/k0s/images/
sudo install -m 0755 bin/k0s /usr/local/bin/k0s
sudo K0S_BINARY=/usr/local/bin/k0s OPERATOR_CHART="$PWD/charts/orama-operator" \
  bin/lake-on-k0s/install.sh
```

`bin/lake-on-k0s/` is the k0s fork's install script with its `Lake` and values, at the fork's pinned
commit. In the bundle it installs CloudNativePG from `charts/` instead of adding a chart repository;
that change to the script is part of building the bundle.

**Your own Kubernetes, with your own registry.** Push every image in `images/images.tar` to your
registry (for example with `skopeo copy --all oci-archive:...` or `crane push`), install the charts
from `charts/`, and set the registry in one place: the operator's image registry setting
(https://github.com/oramasearch/orama-operator/issues/1186) makes every default image come from your
mirror.

## What the stack must do for this to hold

- **No default calls out.** No image, model, host, telemetry endpoint or license check outside the
  bundle. Telemetry is off unless it is turned on.
- **Every image is pinned by digest** in `release.yaml`, so a mirror holds exactly what was checked.
- **The model is local.** The agents and the quickstart run on the model in the bundle
  (https://github.com/oramasearch/zetta-bridge/issues/2), and the weights' licenses allow carrying
  them in.
- **One registry setting** moves every default image to a mirror (https://github.com/oramasearch/orama-operator/issues/1186).

## How it is built

With each stack release, on a connected build host:

1. Read `release.yaml`; refuse to build unless every image has a digest.
2. Pull every image by digest, with `k0s airgap bundle-artifacts`, into `images/images.tar`.
3. Package the charts; copy the binaries built from each component's release tag.
4. Write the SBOMs, the licenses and `checksums.txt`.
5. Sign the checksum and attach the bundle, its checksum and its signature to the release.

If the bundle is larger than the code host's limit for one release file, it is published to object
storage with the same checksum and signature, and the release links to it.
