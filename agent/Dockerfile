FROM mcr.microsoft.com/playwright/python:v1.45.0-jammy

WORKDIR /app

COPY agent/requirements.txt /app/agent/requirements.txt
RUN pip install --no-cache-dir -r /app/agent/requirements.txt

COPY agent /app/agent

CMD ["uvicorn", "agent.main:app", "--host", "0.0.0.0", "--port", "8000"]
