# Install Orama Lake

Two ways to install the first cluster, and they end in the same place: a management cluster running
the operator. From there you declare your Lakes in a `LakeSet`, and the operator runs them.

| You have | Use | What it installs |
|---|---|---|
| A Kubernetes cluster | [The helmfile](#on-a-kubernetes-cluster-you-already-have) | The platform charts and the operator, in one command |
| A fresh Linux machine | [k0s and the helmfile's charts](#on-a-fresh-linux-machine) | Kubernetes itself, then the same charts and the operator, from one script |

Both are followed by the same last step: [declare a `LakeSet`](#run-a-lake-declare-a-lakeset).

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
kubectl get crd lakesets.orama.cloud
```

Then [declare a `LakeSet`](#run-a-lake-declare-a-lakeset).

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
installs the Postgres operator, the certificate manager and the operator's chart, and proves the
machine with one test Lake, printing the address it answers on. `hack/lake-on-k0s/teardown.sh`
removes it. The Lakes you run are declared in a [`LakeSet`](#run-a-lake-declare-a-lakeset).

To run each step yourself, or to install with no network access at all, follow
[`install/k0s.md`](../../modules/orama-operator/docs/install/k0s.md). The air-gapped variant
prepares one image bundle on a connected machine and installs from it with nothing fetched from
outside.

## Run a Lake: declare a LakeSet

You never write a `Lake` yourself. You declare a **`LakeSet`** on the management cluster: one
template, and a list of members. Each member is one Lake on one cluster, in its own namespace. The
management cluster's operator applies every member to its cluster, and that cluster's own operator
runs it. Versions, settings and secrets are managed in one place, for one Lake or for many.

It takes three resources, applied to the management cluster in this order.

### 1. A cluster

A `KubernetesCluster` says what cluster you want. The operator creates it and keeps it as declared.
It names a `KubernetesClusterProvider`, written once per cloud account.

```yaml
apiVersion: orama.cloud/v1alpha1
kind: KubernetesCluster
metadata:
  name: lake-cluster-01
spec:
  providerRef: my-cloud-account
  region: westus2
  kubernetesVersion: "1.35"
  deletionPolicy: Retain
  nodePools:
    - {name: system, role: system, machineSize: Standard_D8as_v7, minCount: 1, maxCount: 5}
  tags:
    purpose: production
```

Every member of one set runs on clusters with the same `purpose` tag, so a set never mixes
production with anything else.

The provider type available today is `aks`. A set's member names a `KubernetesCluster`, so a set
cannot yet place a Lake on a cluster the operator did not create, the management cluster included.

### 2. The platform and the operator on it

A `ClusterHelmRelease` per platform chart, and one `OramaOperator`. They install on the new cluster
exactly what the helmfile installed on the management cluster: the same charts, the same versions,
the same operator.

```yaml
apiVersion: orama.cloud/v1alpha1
kind: OramaOperator
metadata:
  name: lake-cluster-01
spec:
  clusterRef: lake-cluster-01
  version: <operator-version>
```

The charts are listed in the operator's
[sample](../../modules/orama-operator/config/samples/leaf-nonprod-operator.yaml).

### 3. The set

```yaml
apiVersion: orama.cloud/v1alpha1
kind: LakeSet
metadata:
  name: lake-prod
spec:
  template:                    # a Lake's settings, the default for every member
    image: oramasearch/lake:<lake-version>
    ingressEnabled: true
    postgres: {instances: 1, storageSize: 50Gi}
    store: {size: 100Gi, accessModes: [ReadWriteOnce]}
  clusters:                    # the members, independent of each other
    - clusterRef: lake-cluster-01
      name: main
      spec:
        host: lake.example.com
    - clusterRef: lake-cluster-01
      name: team-a             # a dedicated Lake, with its own settings
      spec:
        host: team-a.lake.example.com
        postgres: {instances: 3}
```

Apply it and watch it:

```sh
kubectl apply -f lakeset.yaml
kubectl get lakeset lake-prod
```

The set reports how many members are ready, the version each one runs, and each member's own reason
when it is not ready.

What a set gives you:

| To | Do this |
|---|---|
| Add a Lake | Add a member |
| Upgrade every Lake | Change `template.image` |
| Hold one Lake at a version | Set `image` in that member's `spec` |
| Change one Lake's settings | Set them in that member's `spec`; it is merged over the template |
| Give Lakes their credentials | List the Secrets under `secrets`; the set copies them into each member's namespace |
| Run a Lake in another region | Add a cluster there, and a member on it |

Every field is in the operator's
[resource reference](../../modules/orama-operator/docs/crd-reference.md), and the procedures are in
its [operations guide](../../modules/orama-operator/docs/infrastructure/operations.md) and
[infrastructure guide](../../modules/orama-operator/docs/infrastructure/README.md).

## Remove it

Removing a member from a set, or deleting the set, leaves its Lakes running unless the set says
`deletionPolicy: Delete`. A Lake's volumes are kept when it is deleted; review them before deleting
a claim. A `KubernetesCluster` is destroyed or kept according to its own `deletionPolicy`.

```sh
helm uninstall orama-operator -n orama-system
```
