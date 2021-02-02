FROM python:3.8-slim-buster as python-base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    VENV_PATH="/app/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

FROM python-base as builder-base
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        curl \
        build-essential \
        gcc \
        git \
        g++

ENV POETRY_VERSION=1.1.4
RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python

WORKDIR /app
COPY ./poetry.lock ./pyproject.toml ./

RUN poetry install  --no-root --no-dev
COPY . .
RUN poetry install --no-dev

RUN python -c "import nltk; nltk.download('stopwords')"
RUN mv /root/nltk_data /app/.venv/

FROM python-base as production
COPY --from=builder-base $VENV_PATH $VENV_PATH
ENV PATH="$VENV_PATH:$PATH"

COPY --from=builder-base /app /app

ENTRYPOINT ["topichood"]
