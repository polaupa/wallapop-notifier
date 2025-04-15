FROM python:alpine

WORKDIR /app

COPY wallapop-test.py .

RUN pip install requests

ENV PYTHONUNBUFFERED=1

CMD ["python", "wallapop-test.py"]
