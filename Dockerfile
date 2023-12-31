FROM python:3.11.4-slim-buster

WORKDIR /app
COPY . .

ENV REDIS_HOST="redis"\
    REDIS_AUTH="" \
    REDIS_PORT="6379" \
    REDIS_DATABASE="0" \
    TELEGRAM_BOT_TOKEN="TELEGRAM_BOT_TOKEN" \
    PROGRAM_TYPE="worker" \
    LOG_LEVEL="INFO" \
    MAX_NUM_WORKERS="10" \
    POSTGRES_USER="postgres" \
    POSTGRES_PASSWORD="passwd" \
    POSTGRES_HOST="postgres" \
    POSTGRES_PORT="5432" \
    POSTGRES_DB="postgres"

RUN apt-get update && \
    apt-get install --no-install-recommends -y gcc g++ && \
    pip install --no-cache -r requirements.txt && \
    apt-get purge -y gcc g++ && \
    rm -rf /var/lib/apt/lists/*

ENTRYPOINT /app/entrypoint.sh
