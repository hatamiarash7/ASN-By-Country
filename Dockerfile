# --------------------------
# Builder Stage
# --------------------------
FROM python:3.14-slim AS builder

# --------------------------
# Metadata
# --------------------------
ARG APP_VERSION="undefined@docker"
LABEL org.opencontainers.image.title="asn-by-country" \
    org.opencontainers.image.description="Get ASN delegations list of specific country" \
    org.opencontainers.image.url="https://github.com/hatamiarash7/ASN-By-Country" \
    org.opencontainers.image.source="https://github.com/hatamiarash7/ASN-By-Country" \
    org.opencontainers.image.vendor="hatamiarash7" \
    org.opencontainers.image.authors="hatamiarash7" \
    org.opencontainers.image.version="${APP_VERSION}" \
    org.opencontainers.image.licenses="MIT"

# --------------------------
# Working directory & environment
# --------------------------
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_ROOT_USER_ACTION=ignore \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# --------------------------
# Install dependencies
# --------------------------
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt

# --------------------------
# Runtime Stage
# --------------------------
FROM python:3.14-slim AS runtime

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code (only src directory for modular structure)
COPY src/ ./src/

# Create non-root user and output folder
RUN useradd -m appuser \
    && mkdir -p /app/output_data \
    && chown -R appuser:appuser /app

USER appuser

# Default entrypoint
ENTRYPOINT ["python", "-m", "src.cli"]
