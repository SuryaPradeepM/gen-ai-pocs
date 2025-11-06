FROM python:3.10

WORKDIR /code

COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y portaudio19-dev libreoffice && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--workers", "4", "--host", "0.0.0.0", "--port", "8000"]