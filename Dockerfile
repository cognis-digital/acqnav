# acqnav — Defense Acquisition Navigator.
#
# Pure standard-library CLI; the image just needs Python and the package.
FROM python:3.12-slim

LABEL org.opencontainers.image.title="acqnav" \
      org.opencontainers.image.description="Defense Acquisition Navigator — open, self-hostable acquisition & program-management navigation." \
      org.opencontainers.image.source="https://github.com/cognis-digital/acqnav" \
      org.opencontainers.image.licenses="COCL-1.0"

WORKDIR /app

# Install first (layer cache): copy the package metadata and sources.
COPY pyproject.toml README.md LICENSE ./
COPY acqnav ./acqnav

RUN python -m pip install --no-cache-dir . \
    && python -m acqnav --version

# acqnav makes no network calls at runtime.
ENTRYPOINT ["acqnav"]
CMD ["--help"]
