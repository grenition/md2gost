FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libfreetype6-dev \
    libpng-dev \
    fontconfig \
    fonts-liberation \
    fonts-dejavu-core \
    libreoffice \
    libreoffice-writer \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY md2gost/ /app/md2gost/
COPY setup.py /app/

COPY services/docx-service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir -e /app

RUN mkdir -p /tmp/md2gost

COPY services/docx-service/app.py /app/app.py

ENV PYTHONUNBUFFERED=1
ENV WORKING_DIR=/tmp/md2gost
ENV TEMPLATE_PATH=/app/md2gost/Template.docx

EXPOSE 5000

CMD ["python", "app.py"]

