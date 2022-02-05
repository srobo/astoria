FROM python:3.9-slim as base

WORKDIR /app

RUN pip install --upgrade pip

COPY docker/astoria.toml /etc/
COPY astoria/ /app/astoria
COPY pyproject.toml README.md /app/

RUN pip install .
