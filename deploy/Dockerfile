FROM python:3.11.1-bullseye as python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"


FROM python-base as builder-base

RUN apt-get update && apt-get install -y gcc git

WORKDIR $PYSETUP_PATH

RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir setuptools wheel \
 && pip install --no-cache-dir poetry

COPY ./pyproject.toml ./pyproject.toml

RUN poetry install --without dev


FROM python-base as production

COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

WORKDIR /app
COPY ./alembic.ini /app/alembic.ini
COPY ./src /app/src
