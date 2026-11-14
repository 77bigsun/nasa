FROM python:3.12-slim
WORKDIR /app
COPY services/similarity/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && useradd --create-home app
COPY services/shared /app/services/shared
COPY services/similarity /app/services/similarity
USER app
CMD ["python", "-m", "uvicorn", "services.similarity.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
