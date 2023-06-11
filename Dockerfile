FROM python:3.10.9-alpine3.17 AS builder

COPY . .

RUN apk add --no-cache gcc g++ musl-dev git && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt && \

FROM python:3.10.9-alpine3.17

WORKDIR /app
COPY . .
COPY --from=builder /app/wheels /wheels

ENV REDIS_HOST="redis"\
    REDIS_AUTH="" \
    REDIS_PORT="6379" \
    REDIS_DATABASE="0" \
    TELEGRAM_BOT_TOKEN="TELEGRAM_BOT_TOKEN" \
    PROGRAM_TYPE="worker" \
    LOG_LEVEL="INFO"

RUN pip install --no-cache /wheels/*

ENTRYPOINT entrypoint.sh
