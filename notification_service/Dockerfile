FROM python:3.12-slim-bookworm

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install the application dependencies.
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH="/app"

# Copy dependencies into the container.
COPY pyproject.toml .
COPY uv.lock .
COPY alembic.ini .
RUN uv sync --frozen --no-cache

# Copy the application into the container.
COPY ./notification_service/src ./src
COPY ./notification_service/keys ./keys
COPY ./notification_service/entrypoint.sh .

# Run the application.
ENTRYPOINT ["bash", "entrypoint.sh"]
