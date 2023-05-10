FROM --platform=$BUILDPLATFORM python:3.11.3-slim-buster

ARG APP_VERSION="undefined@docker"

LABEL \
    org.opencontainers.image.title="asn-by-country" \
    org.opencontainers.image.description="Get ASN delegations list of specific country" \
    org.opencontainers.image.url="https://github.com/hatamiarash7/ASN-By-Country" \
    org.opencontainers.image.source="https://github.com/hatamiarash7/ASN-By-Country" \
    org.opencontainers.image.vendor="hatamiarash7" \
    org.opencontainers.image.author="hatamiarash7" \
    org.opencontainers.version="$APP_VERSION" \
    org.opencontainers.image.created="$DATE_CREATED" \
    org.opencontainers.image.licenses="MIT"

WORKDIR /app

COPY ./requirements.txt /app/

RUN pip3 install --no-cache-dir pip &&
    pip3 install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python3", "main.py"]
