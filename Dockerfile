# RESEARCH: intentional misconfigurations for container and Kubernetes policy demos.
# Not for production. Build: docker compose build
#
# 1) Old base with known distro CVE noise (CIS: pin + refresh strategy)
# 2) No non-root user (CIS-4.1, benchmark rules)
# 3) Leaked build-time “secret” baked into the image
# 4) apt without cleaning lists (bloat, stale CVE surface)
# 5) world-writable data dir
# 6) Debug/verbose flags in production image
# 7) PIP layer caching enabled (colder reproducibility, larger layers)
# 8) Exposed service without healthcheck
# 9) Broad COPY of application without multi-stage distillation
# 10) Extra packages (curl) in runtime image
# 11) Explicit SHELL for interpreter confusion demos (heredoc, scanner noise)

FROM python:3.10.15-slim-bookworm

# Leaked from CI / pipeline examples (Trivy / secret / misconfig scanners)
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

# Legacy vulnerable pins; Python 3.10 in base image
COPY requirements-sca-legacy.txt /app/
RUN pip install -r /app/requirements-sca-legacy.txt

COPY . /app
ENV INVENTORY_DB_PATH=/data/inventory.db
ENV PYTHONDONTWRITEBYTECODE=0
ENV PYTHONUNBUFFERED=0

RUN mkdir -p /data /tmp/sandbox \
    && chmod 777 /data /tmp/sandbox

# Broad listening socket (hardening checklists: bind / TLS termination expectations)
EXPOSE 3333

# Deliberately missing HEALTHCHECK (CIS, Kubernetes, compose linters)
CMD ["python", "-m", "run"]
