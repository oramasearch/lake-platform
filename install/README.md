# install

The Orama Lake installer, [`install.sh`](install.sh). It reads the versions from the
[release manifest](../release.yaml) (this checkout's, or `LAKE_RELEASE_MANIFEST`).

| Command | What it does | Guide |
|---|---|---|
| `install.sh try` | The whole stack in one container on a laptop, with a local model, no account and no API key | [Try it](../docs/install/try-it.md) |
| `install.sh status`, `sign-in`, `stop`, `uninstall` | Look after the Try-it container | [Try it](../docs/install/try-it.md#stop-start-remove) |
| `sudo install.sh server` | k0s, the operator and a Lake on this Linux machine, from a checkout | [Run it](../docs/install/run-it.md) |

`try` needs the Try-it image of a published release; until one exists it stops and says so.
