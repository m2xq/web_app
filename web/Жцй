FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt /app/requirements.txt
COPY . /app

RUN pip install --no-cache-dir -r /app/requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]

