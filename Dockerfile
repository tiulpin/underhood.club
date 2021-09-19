FROM python:3.10-rc-slim as app
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
        curl=7.64.0-4+deb10u2 \
        build-essential=12.6 \
        gcc=4:8.3.0-1 \
        git=1:2.20.1-2+deb10u3 \
        g++=4:8.3.0-1
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"
ENV POETRY_VERSION=1.1.6
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python

WORKDIR /app
COPY ./poetry.lock ./pyproject.toml ./
RUN poetry install --no-root --no-dev
COPY . .
RUN poetry install --no-dev
RUN python -c "import nltk; nltk.download('stopwords')"
RUN mv /root/nltk_data /app/.venv/
RUN poetry run python -m spacy download ru_core_news_sm

FROM python:3.10-rc-slim as prod
ENV PATH="$PATH:/app/.venv/bin"
COPY --from=app /app /app
RUN apt-get update \
    && apt-get install --no-install-recommends -y git=1:2.20.1-2+deb10u3 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
RUN git config --global user.email "hey@underhood.club" && git config --global user.name "underhood"
ENTRYPOINT ["underhood"]
