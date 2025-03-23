FROM python:3.11-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ADD . /app
WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*



RUN uv --directory real-estate-etl sync --frozen
RUN uv --directory real-estate-sqlmesh sync --frozen

ENTRYPOINT ["uv","run"]