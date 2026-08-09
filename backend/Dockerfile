FROM python:3.11-slim

# Install PhoneInfoga CLI (official install script)
RUN apt-get update && apt-get install -y curl ca-certificates && \
    curl -sSL https://raw.githubusercontent.com/sundowndev/phoneinfoga/master/support/scripts/install.sh | bash -s -- -b /usr/local/bin && \
    apt-get purge -y curl && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
COPY static/ ./static/

ENV PORT=10000
EXPOSE 10000

CMD ["python", "app.py"]
