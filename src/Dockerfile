FROM python:3.14-slim AS builder

ENV POETRY_VERSION=2.4.1 \
    POETRY_VIRTUALENVS_CREATE=false \
    DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --root-user-action=ignore poetry==$POETRY_VERSION

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --no-interaction --no-ansi


FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN addgroup --system app && adduser --system --ingroup app app

COPY --from=builder /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY src/ .

USER app

CMD ["python", "main.py"]