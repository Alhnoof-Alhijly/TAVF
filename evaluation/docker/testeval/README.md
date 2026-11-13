# TestEval Final Evaluation image

Base: `python:3.12-slim`. Dependency: `sortedcontainers==2.4.0`, restricted to
the SHA-256-verified PyPI wheel, with no additional dependencies or build tools.
Source: https://pypi.org/pypi/sortedcontainers/2.4.0/json

From the project root in local PowerShell:

```powershell
docker build --tag tavf-testeval:py312-sortedcontainers-2.4.0 --file evaluation/docker/testeval/Dockerfile evaluation/docker/testeval
docker image inspect tavf-testeval:py312-sortedcontainers-2.4.0 --format '{{.Id}}'
```

The base tag is mutable. For repeatable rebuilds, record the resolved base digest
and architecture and supply that same digest on subsequent builds:

```powershell
docker build --build-arg 'PYTHON_BASE=python:3.12-slim@sha256:<recorded-base-digest>' --tag tavf-testeval:py312-sortedcontainers-2.4.0 --file evaluation/docker/testeval/Dockerfile evaluation/docker/testeval
```

Record the resulting image ID with evaluation provenance and use that immutable
ID for the evaluation session. Replace the placeholder with a real recorded digest.
The build needs registry/PyPI access; evaluation containers must have no network.
No project source, datasets, artifacts, credentials or host virtual environment
are copied into the image. Its default user is `65534:65534`.

## Existing runtime contract

An image does not enforce Docker runtime resource limits. The evaluation adapter
must retain the existing invocation, changing only the selected image:

- `--rm --pull=never -i`, unique container name, explicit timeout/forced cleanup.
- `--network none --read-only --cap-drop ALL`.
- `--security-opt no-new-privileges --user 65534:65534 --log-driver none`.
- `--cpus 0.5 --memory 128m --memory-swap 128m --pids-limit 16`.
- No host mounts; source and test strings via stdin; `python -I -B`.
- Empty uppercase and lowercase HTTP_PROXY, HTTPS_PROXY, FTP_PROXY, NO_PROXY,
  ALL_PROXY variables, preserving the existing proxy-credential suppression.
- Existing 10-second execution timeout, bounded coverage output and cleanup rules.

Existing validators and coverage evaluators still name `python:3.12-slim`; they
are intentionally unchanged. The independent evaluation adapter must select this
image before dependency-equipped execution. Do not retag it as the stock image.
Building this image does not run generated tests or establish assertion correctness.
