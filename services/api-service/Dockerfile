FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py /app/app.py

ENV PYTHONUNBUFFERED=1
ENV DOCX_SERVICE_URL=http://docx-service:5000
ENV FILE_SERVICE_URL=http://file-service:5002
ENV SESSION_SERVICE_URL=http://session-service:5003

EXPOSE 5001

CMD ["gunicorn", "--workers", "2", "--threads", "4", "--bind", "0.0.0.0:5001", "--timeout", "300", "app:app"]

