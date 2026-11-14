FROM python:3.12-slim
WORKDIR /app
COPY services/catalog/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && useradd --create-home app
COPY services/shared /app/services/shared
COPY services/catalog /app/services/catalog
USER app
CMD ["python", "-m", "uvicorn", "services.catalog.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
