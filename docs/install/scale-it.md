# Scale it: any Kubernetes cluster, from the helmfile

For a platform team with a cluster already: install the platform and the operator from the operator's
helmfile, then declare one `Lake`. The operator runs everything else. From here a cluster can also
become a [management cluster](README.md#management-cluster) that creates and runs others.

> **Status:** tested so far on one managed Kubernetes provider and on the platform's k0s fork.

## Before you start

- Kubernetes 1.29 or later, a default StorageClass, and `kubectl`, Helm 3 and
  [helmfile](https://helmfile.readthedocs.io/).
- A load balancer for Services, if the Lake should answer on a hostname: ingress-nginx, which the
  helmfile installs, takes its address from one.
- A checkout of this repository at a release, for the helmfile and the versions:

```sh
git clone --recurse-submodules --branch v0.1.0 https://github.com/oramasearch/lake-platform.git
cd lake-platform
git -C modules/orama-operator describe --tags                  # the operator version
git -C modules/liquid-bridge/modules/lake describe --tags      # the lake version
```

## 1. The platform and the operator

The operator's [`helmfile.yaml`](https://github.com/oramasearch/orama-operator/blob/main/helmfile.yaml)
is the one way the platform is installed. It holds every chart the operator builds on, at the versions
it is tested with: CloudNativePG for lake's control plane, cert-manager, ingress-nginx, the operators
for the data services a workspace can add (Kafka, ClickHouse, TiDB, Cassandra, Valkey), and
observability (left out below). Then it installs the operator itself. A management cluster and every cluster it manages
are installed from the same file, so they are the same cluster.

```sh
cd modules/orama-operator
helmfile -l 'app!=orama-operator,name!=kube-prometheus-stack,name!=perses' sync --wait --concurrency 1
helmfile -l app=orama-operator sync --wait --set operator.image.tag=$(git describe --tags)
cd ../..
```

**Observability is left out** (`name!=kube-prometheus-stack,name!=perses`). The helmfile's
observability charts pull Orama's own mirrors of their images, which are not distributed. Lake and
the operator work without them: the operator writes its alerting rules and dashboards once the
monitoring CRDs exist, and says in its status that they are missing until then. To add monitoring,
install your own Prometheus stack.

A chart your cluster already provides (its own ingress controller, cert-manager) is turned off in the
helmfile with `installed: false`, never installed a second way.

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
  image: docker.io/oramasearch/lake:v0.9.0
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
| Its own ingress controller | Set ingress-nginx to `installed: false` in the helmfile, and the Lake's ingress class |
| Its own identity provider | Configure single sign-on in lake (OIDC or SAML) once it is up |
| A private registry mirror | Mirror every image in `release.yaml` and its `dependencies`, then follow [air-gapped](air-gapped.md) |
| Its own Postgres | Not yet: the operator runs lake's Postgres with CloudNativePG |

## Upgrade

Check out the next release of this repository (`git checkout vX.Y.Z && git submodule update
--recursive`) and run step 1 again, then change the Lake's `image`. The operator rolls before the lake
image that needs it; the release notes of each stack version say what an upgrade needs.

## What is missing today

- An umbrella chart that installs the helmfile's charts and a Lake in one `helm install`. Until it
  exists, the helmfile is the install.
- Proof on more than one managed Kubernetes provider and on a plain upstream cluster.
