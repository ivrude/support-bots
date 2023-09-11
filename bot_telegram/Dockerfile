FROM python:3.11.3

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VERSION=1.5.1 \
    POETRY_VIRTUALENVS_CREATE=0 \
    POETRY_VIRTUALENVS_IN_PROJECT=1

ARG work_dir="/bot_telegram"

WORKDIR $work_dir

RUN apt update && \
    apt install -y --no-install-recommends \
    nano binutils gettext libproj-dev gcc libgraphviz-dev graphviz && \
    pip install "poetry==$POETRY_VERSION"

COPY $work_dir/pyproject.toml ./

RUN poetry install --no-ansi --no-root

COPY bot_telegram .
CMD ["python", "-m", "main"]

