FROM python:3.12-slim AS base
WORKDIR /app
RUN pip install --no-cache-dir uv

FROM base AS development
COPY pyproject.toml pyproject.toml
RUN uv pip install --system -e ".[dev]"
COPY . .
CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]

FROM base AS production
COPY pyproject.toml pyproject.toml
RUN uv pip install --system .
COPY app/ app/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
