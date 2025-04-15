FROM python:alpine

WORKDIR /app

COPY wallapop.py .

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1

CMD ["python", "wallapop.py"]
