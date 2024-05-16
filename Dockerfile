FROM python:3.10-slim as base

FROM base as builder

RUN apt-get update && apt-get upgrade -y  \
    && apt-get install python3-dev -y  \
    && apt-get install libc-dev  \
    && apt-get install gcc -y

RUN pip install "poetry==1.4.2" && poetry config virtualenvs.in-project true

RUN mkdir /app

WORKDIR /app

COPY pyproject.toml poetry.lock README.md ./

RUN poetry install --no-root

FROM base

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY . /app

WORKDIR /app

EXPOSE 8000

CMD "./start_application.sh"
