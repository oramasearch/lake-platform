# Try it: Orama Lake on a laptop

The whole stack on your own machine: lake, a workspace with its own zetta, and the operator that runs
them, on a local Kubernetes. **No account and no credential:** every image is public. Your data stays
on your machine.

It runs on a single-node Kubernetes on your machine. Pick one:
[k0s](https://k0sproject.io) or [k3s](https://k3s.io), each installed directly on Linux, or run in
Docker on macOS and Windows. Any other local Kubernetes works the same way from step 2 (Docker
Desktop's, kind, minikube).

## Before you start

- **Linux** (amd64 or arm64), or **macOS** or **Windows** with Docker running.
- `kubectl` and Helm 3.
- At least 4 CPUs, 16 GB of memory and 50 GB of free disk. No GPU is needed.
- A checkout of this repository, for the operator chart:

  ```sh
  git clone --recurse-submodules https://github.com/oramasearch/lake-platform.git
  cd lake-platform
  ```

## 1. Start a single-node Kubernetes

**On Linux**, install k0s as a single node, following the
[k0s quick start](https://docs.k0sproject.io/stable/install/):

```sh
curl -sSLf https://get.k0s.sh | sudo sh
sudo k0s install controller --single
sudo k0s start
sudo k0s kubeconfig admin > ~/.kube/orama-lake && export KUBECONFIG=~/.kube/orama-lake
kubectl get nodes
```

**On macOS or Windows**, run k0s in Docker, following
[k0s in Docker](https://docs.k0sproject.io/stable/k0s-in-docker/). The container is privileged,
because Kubernetes runs inside it. On Docker Desktop, the cgroup options are required:

```sh
docker run -d --name k0s --hostname k0s --privileged \
  --cgroupns=host -v /sys/fs/cgroup:/sys/fs/cgroup:rw \
  -v /var/lib/k0s \
  -p 6443:6443 \
  docker.io/k0sproject/k0s:latest
docker exec k0s k0s kubeconfig admin > ~/.kube/orama-lake && export KUBECONFIG=~/.kube/orama-lake
kubectl get nodes
```

**Or k3s on Linux**, following the [k3s quick start](https://docs.k3s.io/quick-start). k3s ships the
`local-path` storage class, so step 2 is not needed:

```sh
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="server --write-kubeconfig-mode=644" sh -
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
kubectl get nodes
```

**Or k3s in Docker on macOS or Windows**, with [k3d](https://k3d.io), which also ships `local-path`:

```sh
k3d cluster create orama-lake
k3d kubeconfig merge orama-lake --kubeconfig-switch-context
kubectl get nodes
```

Wait until the node is `Ready`.

## 2. Add storage, if the cluster has none

A single-node k0s has no storage class (k3s and k3d have one already). The local-path provisioner
gives it one, on the node's disk:

```sh
kubectl apply -f https://raw.githubusercontent.com/rancher/local-path-provisioner/v0.0.31/deploy/local-path-storage.yaml
kubectl annotate storageclass local-path storageclass.kubernetes.io/is-default-class=true
```

## 3. Install the database operator and the Orama operator

```sh
helm repo add cnpg https://cloudnative-pg.github.io/charts
helm upgrade --install cloudnative-pg cnpg/cloudnative-pg \
  --namespace cnpg-system --create-namespace --version 0.29.0 --wait

helm upgrade --install orama-operator modules/orama-operator/chart \
  --namespace orama-system --create-namespace --set operator.replicas=1 --wait
```

The operator chart is the one this checkout pins: orama-operator v0.12.0.

## 4. Create a Lake

```sh
kubectl apply -f - <<'EOF'
apiVersion: orama.cloud/v1alpha1
kind: Lake
metadata:
  name: hello
spec:
  namespace: lake-dev
  image: oramasearch/lake:v0.9.0
  replicas: 1
  store:
    size: 20Gi
    storageClassName: local-path
    accessModes: [ReadWriteOnce]
  env:
    - name: LAKE_LOG_MODE
      value: air-gapped
  postgres:
    instances: 1
    storageSize: 10Gi
    storageClassName: local-path
EOF
```

The operator creates the namespace `lake-dev`, lake's database, lake itself and its first workspace
zetta. Watch it come up:

```sh
kubectl get lake hello -w
kubectl -n lake-dev get pods
```

## 5. Open it

Forward lake's service to your machine:

```sh
kubectl -n lake-dev get services
kubectl -n lake-dev port-forward service/<lake's service> 8080:<its port>
```

Then open `http://localhost:8080`.

## Remove it

- **k0s on Linux:** `sudo k0s stop && sudo k0s reset`
- **k0s in Docker:** `docker rm -f k0s`, then `docker volume prune` to drop its data.
- **k3s on Linux:** `/usr/local/bin/k3s-uninstall.sh`
- **k3d:** `k3d cluster delete orama-lake`

## Next

- To run it for a team, on a server or a small cluster, see [Run it](run-it.md).
- To use it with an agent, run `claude` in this checkout and type `/lake`.

## Not included yet

**A one-command image** that bundles the steps above with every image preloaded (`install/install.sh try`
and the `lake-try` image) is planned. Until it ships, these steps are the way to try Orama Lake on a
laptop.
