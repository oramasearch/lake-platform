# Scale it: any Kubernetes cluster, with Helm

For a platform team with a cluster already: install the operator's chart and the charts it builds on,
then declare one `Lake`. The operator runs everything else. From here a cluster can also become a
[management cluster](README.md#management-cluster) that creates and runs others.

> **Status:** the chart is published with every operator release, but to a private repository, so
> today it needs a registry credential. The steps below are the same once it is public, without the
> credential. Tested so far on one managed Kubernetes provider and on the platform's k0s fork.

## Before you start

- Kubernetes 1.29 or later, a default StorageClass, and `kubectl` and Helm 3.
- An ingress controller if the Lake should answer on a hostname. The operator works with
  ingress-nginx, which step 1 installs if you have none.
- The versions to install: the operator chart and the lake image from the
  [release manifest](../release/README.md) (`orama-operator` and `lake` in `release.yaml`).

```sh
OPERATOR_VERSION=0.11.12     # release.yaml: components[orama-operator].charts[0].version
LAKE_IMAGE=docker.io/oramasearch/lake:v0.8.1   # release.yaml: components[lake].images[0]
```

## 1. The charts the operator builds on

Postgres for lake's control plane (CloudNativePG), certificates (cert-manager) and, if your cluster
has none, an ingress controller. The versions are the ones the operator is tested with; its
[`helmfile.yaml`](https://github.com/oramasearch/orama-operator/blob/main/helmfile.yaml) is the
source for them.

```sh
helm repo add cnpg https://cloudnative-pg.github.io/charts
helm repo add jetstack https://charts.jetstack.io
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

helm upgrade --install cnpg cnpg/cloudnative-pg \
  --namespace cnpg-system --create-namespace --version 0.29.0 --wait
helm upgrade --install cert-manager jetstack/cert-manager \
  --namespace cert-manager --create-namespace --version v1.21.2 --set crds.enabled=true --wait
helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx --create-namespace --version 4.15.1 --wait   # only if you have none
```

The data services a workspace can add (Kafka, ClickHouse, TiDB, Cassandra, Valkey) need their own
operators; the helmfile installs all of them, and a Lake works without them until a workspace asks
for one.

## 2. The operator

```sh
helm upgrade --install orama-operator \
  oci://registry-1.docker.io/oramasearch/orama-operator-chart \
  --version "$OPERATOR_VERSION" \
  --namespace orama-system --create-namespace --wait
```

While the chart and images are private, log Helm in first (`helm registry login registry-1.docker.io`)
and create the pull Secret the chart names
([credentials](https://github.com/oramasearch/orama-operator/blob/main/docs/install/credentials.md)).

The operator is the same on every cluster: the same chart, every resource kind, every controller.
What a cluster does is decided only by the resources you declare on it.

## 3. A Lake

```yaml
apiVersion: orama.cloud/v1alpha1
kind: Lake
metadata:
  name: main
spec:
  namespace: lake
  image: docker.io/oramasearch/lake:v0.8.1
  replicas: 1
  host: lake.example.com
  ingressEnabled: true
  store: {size: 100Gi, accessModes: [ReadWriteOnce]}
  postgres: {instances: 1, storageSize: 50Gi}
```

```sh
kubectl apply -f lake.yaml
kubectl wait lake/main --for=condition=Ready --timeout=15m
curl -fsS https://lake.example.com/readyz
```

`readyz` says lake is up. To check it reaches its data, create a workspace and run one query in it:
a Lake that answers `readyz` but cannot reach a workspace's zetta is not working.

## Use what your cluster already has

| Your cluster has | Do this |
|---|---|
| Its own ingress controller | Skip ingress-nginx and set the Lake's ingress class |
| Its own identity provider | Configure single sign-on in lake (OIDC or SAML) once it is up |
| A private registry mirror | Mirror every image in `release.yaml` and its `dependencies`, then follow [air-gapped](air-gapped.md) |
| Its own Postgres | Not yet: the operator runs lake's Postgres with CloudNativePG |

## Upgrade

Change `OPERATOR_VERSION` and run step 2 again, then change the Lake's `image`. The operator rolls
before the lake image that needs it; the release notes of each stack version say what an upgrade
needs.

## What is missing today

- Public images and chart, so no credential is needed:
  https://github.com/oramasearch/orama-operator/issues/1186
- An umbrella chart that installs step 1, step 2 and a Lake in one `helm install`. Until it exists,
  the steps above, or the [helmfile](README.md#one-cluster), do the same.
- Proof on more than one managed Kubernetes provider and on a plain upstream cluster.
