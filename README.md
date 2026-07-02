# fetchapi

A command-line tool to download data from REST APIs and save the responses as local files.

---

## Overview

`fetchapi` reads a list of API endpoints from a YAML configuration file, authenticates against them using a single set of HTTP Basic Auth credentials, and saves each response to a local file. JSON responses are automatically pretty-printed; any other content type is saved as-is.

It is designed primarily to fire multiple API calls against the same device but nothing stops you from pointing individual entries at other hosts too, as long as they all share the same credentials.

---

## Features

- Fetches data from one or multiple API endpoints in a single run
- Endpoints and authentication credentials are all defined in a simple YAML file
- HTTP Basic Authentication support
- Automatically pretty-prints JSON responses (4-space indentation, UTF-8 preserved)
- Falls back to raw text if the response is not valid JSON
- Skips endpoints that return `401 Unauthorized`, without stopping the whole run
- Handles connection errors, timeouts, and HTTP errors gracefully, per endpoint
- Credentials can be stored in the config file or prompted interactively (with hidden password input)
- Disables SSL certificate warnings, useful for self-signed certificates on internal devices

---

## Requirements

- Python 3.10+
- Uses standard library modules (`argparse`, `json`, `sys`, `pathlib`) plus the following third-party packages: `requests`, `pyyaml`, `pwinput`.

---

## Installation

```bash
git clone https://github.com/pyquerci/fetchapi.git
cd fetchapi
```

Install the third-party packages via pip and run it directly with Python.

### Windows

A pre-compiled Windows executable is included in the repository, built with PyInstaller 6.19.0 using the command:

```bash
pyinstaller --onefile fetchapi.py
```

No Python installation is needed, just download and run `fetchapi.exe`. For convenience, you can add it to a folder in your system `PATH` to invoke it from any directory; for example, I keep mine in `C:\Tools\fetchapi`.

---

## Configuration

`fetchapi` reads its settings from a YAML file (`default.yaml` by default). The file defines optional credentials and a list of `filename: url` pairs to download. Below and example:

```yaml
credentials:
  username: null
  password: null

items:
  vips.json: "https://10.0.0.245/mgmt/tm/ltm/virtual?expandSubcollections=true"
  pools.json: "https://10.0.0.245/mgmt/tm/ltm/pool?expandSubcollections=true"
  nodes.json: "https://10.0.0.245/mgmt/tm/ltm/node?expandSubcollections=true"
  ifs.json: "https://10.0.0.245/mgmt/tm/net/self"
  routes.json: "https://10.0.0.245/mgmt/tm/net/route"
  dcs.json: "https://10.0.0.245/mgmt/tm/sys/file/ssl-cert"
  vstats.json: "https://10.0.0.245/mgmt/tm/ltm/virtual/stats"
  pstats.json: "https://10.0.0.245/mgmt/tm/ltm/pool/members/stats"
```

It targets a F5 BIG-IP device's iControl REST API, but the file is fully customizable for any REST API that supports HTTP Basic Auth.

- If `username` or `password` are left as `null`, `fetchapi` will prompt for them interactively (the password input is masked).
- The credentials, whether provided in the YAML file or entered interactively, **are shared across all** endpoints in a single run.
- Each key under `items` is the local filename the response will be saved to; each value is the full URL to fetch.
- The example targets a single F5 BIG-IP host, but the URLs listed under `items` can just as well point to multiple different devices, as long as they all share the same credentials.

---

## Usage

```
fetchapi.py [-h]
            [-a]
            [-c CONFIG]
```

### Arguments

| Argument | Description |
|---|---|
| `-h, --help` | Show the help message and exit. |
| `-a, --about` | Show author, version, project URL and license information. |
| `-c, --config CONFIG` | YAML configuration file to use. Defaults to `default.yaml` in the current directory. |

### Examples

```bash
# Run using the default configuration file (default.yaml)
fetchapi.py

# Run using a custom configuration file
fetchapi.py -c D:\Home\Desktop\bigip01.yaml

# Show author and version information
fetchapi.py -a
```

---

## How It Works

For each `filename: url` pair defined in the `items` section of the config file, `fetchapi`:

1. Sends an HTTP GET request to the URL, authenticating with the provided credentials.
2. If the server responds with `401 Unauthorized`, the endpoint is skipped and `fetchapi` moves on to the next one.
3. On any other error status, or on connection/timeout errors, the error is printed and the next endpoint is processed.
4. On success, the response body is parsed as JSON and re-serialized with indentation for readability . If the response is not valid JSON, the raw text is saved instead.
5. The result is written to the corresponding local file.

SSL certificate verification is disabled by design.

---

## Production Testing

`fetchapi` has been used to retrieve all the API endpoints required by [`f5report`](https://github.com/pyquerci/f5report), a reporting tool for F5 BIG-IP devices, across several production machines. No issues were encountered during its use.

---

## License

This project is licensed under the **GNU General Public License v2.0 (GPLv2)**. You are free to use, modify, and distribute this software under the terms of that license. See the [LICENSE](LICENSE) file for the full license text.

---

## Donations

If you value the work and want to help support its development, feel free to make a donation. Your support will be greatly appreciated:

- PayPal: https://paypal.me/pyquerci
- Buy Me a Coffee: https://buymeacoffee.com/pyquerci
