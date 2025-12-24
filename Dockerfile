FROM ghcr.io/astral-sh/uv:latest as base

WORKDIR /app

COPY docker/astoria.toml /etc/
COPY astoria/ /app/astoria
COPY pyproject.toml uv.lock README.md /app/

RUN uv sync
