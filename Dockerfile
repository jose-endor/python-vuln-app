# RESEARCH: intentional misconfigurations for container and Kubernetes policy demos.
# Not for production. Build: docker compose build
#
# Multi-stage: (A) Node builds React 17 + TS app → static/app (B) Python image (same bad practices as before)

FROM node:18-bullseye-slim AS frontend
WORKDIR /build/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build
# Vite outDir: ../static/app from frontend/
RUN test -f /build/static/app/index.html

# Leaked from CI / pipeline examples (Trivy / secret / misconfig scanners)
FROM python:3.10.15-slim-bookworm
ARG INSECURE_BUILD_ARG=leaked-pipeline-secret-RESEARCH-STATIC
ARG EXTRA_BAD_TOKEN=hardcoded-ghp_fake_token_for_demos_1234
ENV BOOKSTORE_SECRET_KEY=super-secret-embedded-in-image-RESEARCH-ONLY
ENV PIP_NO_CACHE_DIR=0
ENV LEAKED_BUILD_ENV=${INSECURE_BUILD_ARG}
ENV EXTRA_BAD_TOKEN=${EXTRA_BAD_TOKEN}
ENV FLASK_DEBUG=1
ENV PORT=3333

USER root
WORKDIR /app
SHELL ["/bin/sh", "-c"]

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && echo "intentionally not running rm -rf /var/lib/apt/lists/* for SCA/scan demos"

COPY requirements-sca-legacy.txt /app/
RUN pip install -r /app/requirements-sca-legacy.txt

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
