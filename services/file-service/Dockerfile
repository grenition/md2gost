FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py /app/app.py

RUN mkdir -p /tmp/md2gost/sessions

ENV PYTHONUNBUFFERED=1
ENV STORAGE_BASE=/tmp/md2gost/sessions

EXPOSE 5002

CMD ["python", "app.py"]

