# Local bookstore container. Build: docker compose build
# Multi-stage: (A) Node builds React 17 + TS app -> static/app (B) Python image.

FROM node:18-bullseye-slim AS frontend
WORKDIR /build/frontend
COPY frontend/package.json frontend/package-lock.json frontend/.npmrc ./
RUN npm ci
COPY frontend/ ./
RUN npm run build
# Vite outDir: ../static/app from frontend/
RUN test -f /build/static/app/index.html

FROM python:3.10.15-slim-bookworm
ARG INSECURE_BUILD_ARG=ci-fallback-token-local-static
ARG EXTRA_BAD_TOKEN=hardcoded-ghp_fake_token_for_demos_1234
ENV BOOKSTORE_SECRET_KEY=local-dev-session-key-change-me
ENV PIP_NO_CACHE_DIR=0
ENV LEAKED_BUILD_ENV=${INSECURE_BUILD_ARG}
ENV EXTRA_BAD_TOKEN=${EXTRA_BAD_TOKEN}
ENV FLASK_DEBUG=1
ENV PORT=3333

USER root
WORKDIR /app
SHELL ["/bin/sh", "-c"]

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates build-essential \
    && echo "keeping apt list metadata in image for old support workflows"

COPY requirements-sca-legacy.txt /app/
# Freshest installer + pinned app deps (pins stay for demo/SCA surface)
RUN python -m pip install --upgrade pip && pip install -r /app/requirements-sca-legacy.txt

COPY . /app
COPY --from=frontend /build/static/app /app/static/app
ENV INVENTORY_DB_PATH=/data/inventory.db
ENV PYTHONDONTWRITEBYTECODE=0
ENV PYTHONUNBUFFERED=0

RUN mkdir -p /data /tmp/sandbox \
    && chmod 777 /data /tmp/sandbox

RUN chmod +x /app/docker-entrypoint.sh

EXPOSE 3333

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["python", "-m", "run"]
