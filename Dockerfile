FROM python:3.9-slim-buster as app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    VENV_PATH="/app/.venv"
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        curl \
        build-essential \
        gcc \
        git \
        g++
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"
ENV POETRY_VERSION=1.1.6
RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python

WORKDIR /app
COPY ./poetry.lock ./pyproject.toml ./
RUN poetry install --no-root --no-dev
COPY . .
RUN poetry install --no-dev
RUN python -c "import nltk; nltk.download('stopwords')"
RUN mv /root/nltk_data /app/.venv/
RUN poetry run python -m spacy download ru_core_news_sm

FROM python:3.9-slim-buster as production
ENV PATH="$PATH:/app/.venv/bin"
COPY --from=app /app /app
RUN apt-get update \
    && apt-get install --no-install-recommends -y git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
RUN git config --global user.email "hey@underhood.club" && git config --global user.name "underhood"
ENTRYPOINT ["underhood"]
