# GPT4Free_tg_bot

Telegram bot for generating text with g4f.

## Metrics

[Dashboard](https://github.com/OldTyT/gpt4free_tg_bot/blob/master/grafana/gpt4free_tg_bot.json) was prepared for data visualization in grafana.

## Environment variables

|Variable|What is it|Default value|
|---|---|---|
| `REDIS_HOST` | Redis host | `redis` |
| `REDIS_AUTH` | Redis auth | `""` |
| `REDIS_PORT` | Redis port | `6379` |
| `REDIS_DATABASE` | Redis database | `0` |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | `TELEGRAM_BOT_TOKEN` |
| `PROGRAM_TYPE` | Program type. [See for more](https://github.com/OldTyT/gpt4free_tg_bot/blob/master/entrypoint.sh).| `worker` |
| `LOG_LEVEL` | Log level | `INFO` |
| `MAX_NUM_WORKERS` | Active process workers | `10` |
| `POSTGRES_USER` | Postgres user | `postgres` |
| `POSTGRES_PASSWORD` | Postgres password | `passwd` |
| `POSTGRES_HOST` | Postgres host | `postgres` |
| `POSTGRES_PORT` | Postgres port | `5432` |
| `POSTGRES_DB` | Postgres database | `postgres` |

## TODO

* Markdown validator after generate text.
