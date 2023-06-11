FROM python:3.11.4-slim-buster

WORKDIR /app
COPY . .

ENV REDIS_HOST="redis"\
    REDIS_AUTH="" \
    REDIS_PORT="6379" \
    REDIS_DATABASE="0" \
    TELEGRAM_BOT_TOKEN="TELEGRAM_BOT_TOKEN" \
    PROGRAM_TYPE="worker" \
    LOG_LEVEL="INFO"

RUN  pip install --no-cache -r requirements.txt

ENTRYPOINT /app/entrypoint.sh
