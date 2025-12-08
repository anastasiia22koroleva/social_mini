
FROM python:3.12-slim AS dependencies

RUN pip install --upgrade pip && pip install poetry

WORKDIR /app


COPY pyproject.toml poetry.lock ./


RUN poetry install --no-root --only=main


FROM python:3.12-slim


RUN pip install poetry

WORKDIR /app


COPY --from=dependencies /root/.cache/pypoetry /root/.cache/pypoetry


COPY . .


CMD ["poetry", "run", "uvicorn", "social_mini.main:app", "--host", "0.0.0.0", "--port", "8000"]