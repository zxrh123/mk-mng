# syntax=docker/dockerfile:1.7

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml ./
RUN pip install --upgrade pip && \
    python - <<'PY' > requirements.txt
import tomllib
from pathlib import Path

data = tomllib.loads(Path('pyproject.toml').read_text())
for dep in data['project']['dependencies']:
    print(dep)
PY
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt && pip install --no-cache-dir uvicorn

COPY app ./app

CMD ["python", "-m", "app"]

