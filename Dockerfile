FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app:/app/engine \
    ARE_BACKEND_HOST=0.0.0.0 \
    ARE_BACKEND_PORT=8000

COPY pyproject.toml build_backend.py README.md ./
COPY backend ./backend
COPY engine ./engine
COPY scripts ./scripts
COPY data ./data
COPY fastapi ./fastapi
COPY pydantic ./pydantic
COPY pydantic_settings ./pydantic_settings
COPY openpyxl ./openpyxl
COPY uvicorn ./uvicorn
COPY yaml.py ./yaml.py

RUN python -m pip install --upgrade pip && python -m pip install -e .[dev]

EXPOSE 8000

CMD ["python", "scripts/run_backend.py"]
