FROM python:3.9.5-slim-buster

WORKDIR /app

COPY ./requirements.txt /app

RUN pip3 install -r requirements.txt

COPY . .

ENTRYPOINT ["python3", "main.py"]