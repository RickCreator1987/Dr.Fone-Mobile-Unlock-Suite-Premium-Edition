FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml ./
COPY src ./src
COPY README.md ./

RUN pip install --no-cache-dir .

RUN useradd --create-home --shell /usr/sbin/nologin mss \
    && mkdir -p /data \
    && chown -R mss:mss /app /data

USER mss

VOLUME ["/data"]
WORKDIR /data

ENTRYPOINT ["mss"]
CMD ["--help"]