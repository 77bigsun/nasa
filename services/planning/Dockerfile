FROM python:3.12-slim
WORKDIR /app
COPY services/planning/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && useradd --create-home app
COPY services/shared /app/services/shared
COPY services/planning /app/services/planning
USER app
CMD ["python", "-m", "uvicorn", "services.planning.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
