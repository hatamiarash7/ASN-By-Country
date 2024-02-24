FROM --platform=$BUILDPLATFORM python:3.11.4-slim-buster

ARG APP_VERSION="undefined@docker"

LABEL org.opencontainers.image.title="asn-by-country"
LABEL org.opencontainers.image.description="Get ASN delegations list of specific country"
LABEL org.opencontainers.image.url="https://github.com/hatamiarash7/ASN-By-Country"
LABEL org.opencontainers.image.source="https://github.com/hatamiarash7/ASN-By-Country"
LABEL org.opencontainers.image.vendor="hatamiarash7"
LABEL org.opencontainers.image.author="hatamiarash7"
LABEL org.opencontainers.version="$APP_VERSION"
LABEL org.opencontainers.image.created="$DATE_CREATED"
LABEL org.opencontainers.image.licenses="MIT"

WORKDIR /app

COPY ./requirements.txt /app/

RUN pip3 install --no-cache-dir pip \
    && pip3 install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python3", "main.py"]
