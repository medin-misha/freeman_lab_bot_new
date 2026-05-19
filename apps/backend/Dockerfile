FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .
RUN chmod +x docker-entrypoint.sh

EXPOSE 8000
ENTRYPOINT [ "./docker-entrypoint.sh" ]
