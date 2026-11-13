# Supply a python:3.12-slim digest via PYTHON_BASE to freeze the base image.
ARG PYTHON_BASE=python:3.12-slim
FROM ${PYTHON_BASE}

COPY requirements.txt /opt/testeval/requirements.txt
RUN python -m pip install --no-cache-dir --disable-pip-version-check \
    --no-deps --only-binary=:all: --require-hashes \
    -r /opt/testeval/requirements.txt

USER 65534:65534
CMD ["python", "-I", "-B"]
