FROM python:3.10-slim-bullseye as app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    VENV_PATH="/app/.venv" \
    POETRY_VERSION=1.1.12
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
        curl=7.74.0-1.3+deb11u1 \
        build-essential=12.9 \
        git=1:2.30.2-1 && \
    curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app
COPY ./poetry.lock ./pyproject.toml ./
RUN poetry install --no-root --no-dev
COPY . .
RUN poetry install --no-dev && \
    python -c "import nltk; nltk.download('stopwords')" && \
    mv /root/nltk_data /app/.venv/ && \
    poetry run python -m spacy download ru_core_news_sm

FROM python:3.10-slim-bullseye as prod
ENV PATH="$PATH:/app/.venv/bin"
COPY --from=app /app /app
RUN apt-get update \
    && apt-get install --no-install-recommends -y git=1:2.30.2-1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
RUN git config --global user.email "viktor@tiulp.in" && git config --global user.name "tiulpin"
ENTRYPOINT ["underhood"]
