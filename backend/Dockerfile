FROM python:3.11-slim

WORKDIR /app

# Install PhoneInfoga using the project's official installer script.
# The script needs curl (to fetch the release) and tar (to unpack it),
# and sha256sum (already present in debian slim) to verify the checksum.
RUN apt-get update && apt-get install -y --no-install-recommends curl tar ca-certificates && \
    curl -sSL https://raw.githubusercontent.com/sundowndev/phoneinfoga/master/support/scripts/install | bash && \
    mv ./phoneinfoga /usr/local/bin/phoneinfoga && \
    chmod +x /usr/local/bin/phoneinfoga && \
    apt-get purge -y curl && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
COPY static/ ./static/

ENV PORT=10000
EXPOSE 10000

CMD ["python", "app.py"]
