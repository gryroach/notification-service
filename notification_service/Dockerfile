FROM python:3.12-slim-bookworm

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install the application dependencies.
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH="./src"

# Copy dependencies into the container.
COPY pyproject.toml .
COPY uv.lock .
COPY alembic.ini .
RUN uv sync --frozen --no-cache --no-group dev

# Copy the application into the container.
COPY ./notification_service/src .
COPY ./notification_service/keys ./keys
COPY ./notification_service/entrypoint.sh .

# Run the application.
ENTRYPOINT ["bash", "entrypoint.sh"]
