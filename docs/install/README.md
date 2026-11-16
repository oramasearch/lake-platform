# Install Orama Lake

Four ways in, from a laptop to a network with no way out. Every one installs the same stack, through
the same operator, at the versions in one [release manifest](../release/README.md).

| | Where | Page |
|---|---|---|
| **Try it** | A laptop: a single-node k0s or k3s (directly on Linux, in Docker on macOS and Windows), the operator and one Lake; no account, no credential | [`try-it.md`](try-it.md) |
| **Run it** | One Linux machine or a small cluster, with k0s and the operator | [`run-it.md`](run-it.md) |
| **Scale it** | Any Kubernetes cluster, with the operator's Helm chart | [`scale-it.md`](scale-it.md) |
| **Air-gapped** | One signed bundle, nothing fetched from outside | [`air-gapped.md`](air-gapped.md) (a design) |

The rest of this page is the install from a checkout with the helmfile, which is how the platform is
installed today. Pick one of its two forms. Both install the same operator from the same helmfile, so a
one-cluster install can grow into a management cluster later.

| | What you get | Use it for |
|---|---|---|
| [**One cluster**](#one-cluster) | Everything on a single cluster: the operator and a Lake | Trying it, a small team, one machine, an air-gapped box |
| [**Management cluster**](#management-cluster) | One cluster that creates and runs others, with your Lakes on dedicated clusters | Production, several regions, a Lake per team or customer |

## Before you start

Get the source, and read the versions that work together from its pins:

```sh
git clone https://github.com/oramasearch/lake-platform.git
cd lake-platform
git submodule update --init modules/orama-operator modules/liquid-bridge
git -C modules/liquid-bridge submodule update --init modules/lake modules/k0s

git -C modules/orama-operator describe --tags               # <operator-version>
git -C modules/liquid-bridge/modules/lake describe --tags   # <lake-version>
```

If your registry needs a credential to pull the images, create the pull Secret first
([credentials](https://github.com/oramasearch/orama-operator/blob/main/docs/install/credentials.md)).

## One cluster

### On a Kubernetes cluster you already have

You need Kubernetes 1.29 or later, a default StorageClass, and `kubectl`, Helm 3 and
[helmfile](https://helmfile.readthedocs.io/).

**1. Install the platform and the operator.**

```sh
cd modules/orama-operator
helmfile -l app!=orama-operator sync --wait --concurrency 1
helmfile -l app=orama-operator sync --wait --set operator.image.tag=<operator-version>
```

**2. Run a Lake.** Save this as `lake.yaml`:

```yaml
apiVersion: orama.cloud/v1alpha1
kind: Lake
metadata:
  name: main
spec:
  namespace: lake
  image: oramasearch/lake:<lake-version>
  replicas: 1
  store: {size: 100Gi, accessModes: [ReadWriteOnce]}
  postgres: {instances: 1, storageSize: 50Gi}
```

```sh
kubectl apply -f lake.yaml
kubectl wait lake/main --for=condition=Ready --timeout=15m
```

**3. Open it.**

```sh
kubectl -n lake port-forward service/lake-main 4900:80
curl -fsS http://127.0.0.1:4900/readyz
```

For a public address, add `ingressEnabled: true` and `host` to the Lake.

### On a fresh Linux machine

No cluster yet: one script installs Kubernetes (the k0s distribution this platform ships), the
platform, the operator and a Lake, and prints the address it answers on. You need a Linux host with
no existing `/var/lib/k0s`, and Git, curl, Helm 3, GNU Make and Go.

```sh
cd modules/liquid-bridge/modules/k0s
sudo OPERATOR_CHART="$OLDPWD/modules/orama-operator/chart" hack/lake-on-k0s/install.sh
```

`hack/lake-on-k0s/teardown.sh` removes it. To install with no network access at all, see [air-gapped](air-gapped.md). [Run it](run-it.md) has the
same install with more detail.

## Management cluster

The management cluster runs no Lake of its own. You declare clusters and Lakes on it as resources,
and its operator creates them and keeps them as declared. You never write a `Lake` here: a
**`LakeSet`** does it, for one Lake or for many.

**1. Install the platform and the operator** on the cluster that will manage the others. It is the
same step as above:

```sh
cd modules/orama-operator
helmfile -l app!=orama-operator sync --wait --concurrency 1
helmfile -l app=orama-operator sync --wait --set operator.image.tag=<operator-version>
```

**2. Declare a cluster.** The operator creates it, then installs the same platform and the same
operator on it. Save as `cluster.yaml` and `kubectl apply -f` it:

```yaml
apiVersion: orama.cloud/v1alpha1
kind: KubernetesCluster
metadata:
  name: lake-cluster-01
spec:
  providerRef: my-cloud-account      # a KubernetesClusterProvider, written once per account
  region: westus2
  kubernetesVersion: "1.35"
  deletionPolicy: Retain
  nodePools:
    - {name: system, role: system, machineSize: Standard_D8as_v7, minCount: 1, maxCount: 5}
  tags:
    purpose: production
---
apiVersion: orama.cloud/v1alpha1
kind: OramaOperator
metadata:
  name: lake-cluster-01
spec:
  clusterRef: lake-cluster-01
  version: <operator-version>
```

The provider and the platform charts for the new cluster are in the operator's samples:
[the provider and cluster](https://github.com/oramasearch/orama-operator/blob/main/config/samples/kubernetescluster-nonprod.yaml),
[the charts and operator](https://github.com/oramasearch/orama-operator/blob/main/config/samples/leaf-nonprod-operator.yaml).
The provider type available today is `aks`.

**3. Declare your Lakes.** One template, and a list of members. Each member is one Lake on one
cluster, in its own namespace. Save as `lakeset.yaml` and `kubectl apply -f` it:

```yaml
apiVersion: orama.cloud/v1alpha1
kind: LakeSet
metadata:
  name: lake-prod
spec:
  template:                    # the default for every member
    image: oramasearch/lake:<lake-version>
    ingressEnabled: true
    postgres: {instances: 1, storageSize: 50Gi}
    store: {size: 100Gi, accessModes: [ReadWriteOnce]}
  clusters:
    - clusterRef: lake-cluster-01
      name: main
      spec: {host: lake.example.com}
    - clusterRef: lake-cluster-01
      name: team-a             # a dedicated Lake, with its own settings
      spec:
        host: team-a.lake.example.com
        postgres: {instances: 3}
```

```sh
kubectl get lakeset lake-prod
```

From then on, everything is a change to the set:

| To | Do this |
|---|---|
| Add a Lake | Add a member |
| Upgrade every Lake | Change `template.image` |
| Hold one Lake at a version | Set `image` in that member's `spec` |
| Run a Lake in another region | Declare a cluster there, and add a member on it |

A set's members run on clusters the operator created. It cannot yet place a Lake on the management
cluster itself, which is why the one-cluster install writes its Lake directly.

## More

The full procedures, with every check and every failure to look for, are the operator's:

- [The helmfile install, step by step](https://github.com/oramasearch/orama-operator/blob/main/docs/install.md)
- [A fresh machine with k0s, and air-gapped](https://github.com/oramasearch/orama-operator/blob/main/docs/install/k0s.md)
- [Clusters, sets and day-to-day operations](https://github.com/oramasearch/orama-operator/blob/main/docs/infrastructure/operations.md)
- [Every resource and field](https://github.com/oramasearch/orama-operator/blob/main/docs/crd-reference.md)
