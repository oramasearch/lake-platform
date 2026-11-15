# Run it: one machine or a small cluster, with k0s

For a server, a homelab or a team on one machine: Kubernetes from the platform's k0s fork, the
operator, and a Lake, installed as services on a Linux host. Add machines later to make it a small
cluster.

> **Status:** the script exists and is written from the operator's procedure, but it has not yet been
> run end to end on a clean host. It builds k0s from source, and while the images are private it
> needs a registry credential. The packaged form (a k0s binary from the release, no source checkout,
> no credential) follows the stack release.

## Before you start

- A Linux host (amd64 or arm64) supported by k0s, with no existing `/var/lib/k0s`.
- Root access, and Git, curl, Helm 3, GNU Make and Go (Go and Make only while k0s is built from
  source; set `K0S_BINARY` to a built binary to skip them).
- At least 4 CPUs, 16 GB of memory and 100 GB of disk for one Lake.
- While the images are private: a pull-only registry credential in `ORAMA_DOCKERHUB_USERNAME` and
  `ORAMA_DOCKERHUB_TOKEN`. The script checks anonymously first and skips the credential once the images
  are public.

## Install

```sh
git clone https://github.com/oramasearch/lake-platform.git
cd lake-platform
git submodule update --init modules/orama-operator modules/liquid-bridge
git -C modules/liquid-bridge submodule update --init modules/k0s

sudo install/install.sh server
```

While the images are private, keep the credential across `sudo` without writing it anywhere:

```sh
read -r -s ORAMA_DOCKERHUB_TOKEN; export ORAMA_DOCKERHUB_TOKEN ORAMA_DOCKERHUB_USERNAME=<user>
sudo --preserve-env=ORAMA_DOCKERHUB_USERNAME,ORAMA_DOCKERHUB_TOKEN install/install.sh server
```

`install.sh server` runs the k0s fork's
[`hack/lake-on-k0s/install.sh`](https://github.com/oramasearch/k0s/blob/liquid/hack/lake-on-k0s/install.sh)
with the operator chart from this checkout. It:

1. builds or takes the k0s binary and starts it as a controller with a worker;
2. waits for Kubernetes and for the fork's components (Cilium, Gateway API, local-path);
3. installs CloudNativePG and the operator;
4. applies one `Lake` and a route to it, and prints the address it answers on.

To remove it: `sudo modules/liquid-bridge/modules/k0s/hack/lake-on-k0s/teardown.sh`.

## Give it a name and TLS

Point a DNS name at the host, then set `host` and `ingressEnabled: true` on the `Lake`, and the
operator issues its certificate. The `Lake` resource is the place to change it, never the pods:

```sh
sudo k0s kubectl edit lake hello
```

## Grow to a small cluster

Each extra machine joins as a k0s worker, and the operator spreads workspace zettas over the nodes:

```sh
sudo k0s token create --role=worker > worker-token     # on the first machine
sudo k0s install worker --token-file worker-token && sudo k0s start   # on each new machine
```

## Versions

The versions are the ones this checkout pins, and the [release manifest](../release/README.md)
lists them. To upgrade, check out the next release and run the operator's upgrade from its chart;
the release notes say what each upgrade needs.

## The full procedure

The operator's [k0s guide](https://github.com/oramasearch/orama-operator/blob/main/docs/install/k0s.md)
has every step the script takes, with the checks for each, and the
[air-gapped variant](air-gapped.md).
