# Install Orama Lake

Two ways to install, and they end in the same place: a Kubernetes cluster running the operator, and
one `Lake` that the operator keeps running.

| You have | Use | What it installs |
|---|---|---|
| A Kubernetes cluster | [The helmfile](#on-a-kubernetes-cluster-you-already-have) | The platform charts and the operator, in one command |
| A fresh Linux machine | [k0s and the helmfile's charts](#on-a-fresh-linux-machine) | Kubernetes itself, then the same charts and the operator, from one script |

Both are followed by the same last step: [apply one `Lake`](#apply-one-lake).

This page is the short form. The full procedures, with every check and every failure to look for,
are in the operator's own documents:

- [`install.md`](../../modules/orama-operator/docs/install.md): the helmfile path, step by step
- [`install/k0s.md`](../../modules/orama-operator/docs/install/k0s.md): a fresh machine, and the
  air-gapped variant
- [`install/credentials.md`](../../modules/orama-operator/docs/install/credentials.md): pull
  credentials, and what to check when a pod does not start

## Before you start

- **The source**, with the operator checked out:

  ```sh
  git clone https://github.com/oramasearch/lake-platform.git
  cd lake-platform
  git submodule update --init modules/orama-operator
  ```

- **The versions.** A commit of this repository is one set of versions that work together. Read them
  from the pins and use them wherever this page says `<operator-version>` and `<lake-version>`:

  ```sh
  git -C modules/orama-operator describe --tags          # the operator
  git submodule update --init modules/liquid-bridge
  git -C modules/liquid-bridge submodule update --init modules/lake
  git -C modules/liquid-bridge/modules/lake describe --tags   # lake
  ```

- **Access to the images.** If your registry needs a credential to pull `oramasearch/orama-operator`
  and `oramasearch/lake`, create a pull Secret in each namespace that runs them
  ([`install/credentials.md`](../../modules/orama-operator/docs/install/credentials.md)). An
  air-gapped install carries the images in a bundle instead.

## On a Kubernetes cluster you already have

You need Kubernetes 1.29 or later, a default StorageClass, and `kubectl`, Helm 3 and
[helmfile](https://helmfile.readthedocs.io/) on your machine.

Pin the operator's version in a values file:

```sh
cd modules/orama-operator
cat > operator-values.yaml <<EOF
operator:
  image:
    repository: oramasearch/orama-operator
    tag: "<operator-version>"
EOF
```

Install the platform charts, then the operator:

```sh
helmfile -l app!=orama-operator sync --wait --concurrency 1
helmfile -l app=orama-operator sync --values "$PWD/operator-values.yaml" --wait
```

The first command installs what the operator builds on, each chart pinned to a version in
`helmfile.yaml`: the Postgres operator, the ingress controller, the certificate manager, the
operators for the managed data services, and monitoring. If your cluster already provides one of
them, leave it out with a selector
([`install.md`](../../modules/orama-operator/docs/install.md#1-prepare-registry-access-and-platform-controllers)).
The second installs the operator with all of its resource kinds.

Check it:

```sh
kubectl -n orama-system rollout status deployment/orama-operator --timeout=10m
kubectl get crd lakes.orama.cloud
```

Then [apply one `Lake`](#apply-one-lake).

## On a fresh Linux machine

Use this when there is no cluster yet: one machine, or the first machine of a small cluster. It
installs the k0s distribution this platform ships, which brings the networking, the gateway and the
local storage class the rest expects. A stock k0s binary is not a substitute.

You need a dedicated Linux host with no existing `/var/lib/k0s`, and Git, curl, Helm 3, GNU Make and
Go on it.

```sh
git -C modules/liquid-bridge submodule update --init modules/k0s
cd modules/liquid-bridge/modules/k0s
sudo OPERATOR_CHART="$OLDPWD/modules/orama-operator/chart" hack/lake-on-k0s/install.sh
```

The script builds and installs k0s, waits for the node and every component of the distribution,
installs the Postgres operator, the certificate manager and the operator's chart, applies one `Lake`
and prints the address it answers on. `hack/lake-on-k0s/teardown.sh` removes it.

To run each step yourself, or to install with no network access at all, follow
[`install/k0s.md`](../../modules/orama-operator/docs/install/k0s.md). The air-gapped variant
prepares one image bundle on a connected machine and installs from it with nothing fetched from
outside.

## Apply one Lake

A `Lake` is one resource. From it the operator creates the lake service, its control database, its
store, and the engine each workspace gets.

```yaml
apiVersion: orama.cloud/v1alpha1
kind: Lake
metadata:
  name: hello
spec:
  namespace: lake
  image: oramasearch/lake:<lake-version>
  replicas: 1
  store:
    size: 100Gi
    accessModes:
      - ReadWriteOnce
  postgres:
    instances: 1
    storageSize: 50Gi
```

Save it as `lake.yaml`, then apply it. The operator creates the namespace:

```sh
kubectl apply -f lake.yaml
kubectl wait lake/hello --for=condition=Ready --timeout=15m
kubectl get lake hello
```

Ready means the row reports `READY=1`, `DB=1/1`, `SCHEMA=Applied` and `PHASE=Ready`. To reach it
from your machine:

```sh
kubectl -n lake port-forward service/lake-hello 4900:80
curl -fsS http://127.0.0.1:4900/readyz
```

What to change for a real installation:

| For | Set |
|---|---|
| More than one replica | `replicas`, and a store with `ReadWriteMany` on replicated storage |
| A public address | `ingressEnabled: true` and `host`, with a TLS Secret in the namespace |
| A registry that needs a credential | `pullSecretName` |
| No outside connections at all | `env` with `LAKE_LOG_MODE: air-gapped`, and no `host` |
| Backups of the control database | `postgres.backup` |

Every field is in the operator's
[resource reference](../../modules/orama-operator/docs/crd-reference.md).

## After the first cluster

The cluster you just installed can manage others. Declare a cluster as a resource and the operator
creates it, installs the same charts and the same operator on it, and keeps them reconciled. That is
how one management cluster runs many dedicated leaf clusters
([the operator's infrastructure guide](../../modules/orama-operator/docs/infrastructure/README.md)).

## Remove it

```sh
kubectl delete lake hello
helm uninstall orama-operator -n orama-system
```

The Lake's volumes are kept when the `Lake` is deleted. Review them before deleting a claim.
