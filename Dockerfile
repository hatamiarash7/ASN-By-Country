FROM python:3.11.1-slim-buster

WORKDIR /app

COPY ./requirements.txt /app

RUN pip3 install -r requirements.txt

COPY . .

ENTRYPOINT ["python3", "main.py"]