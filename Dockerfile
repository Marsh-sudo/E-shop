# official base image
FROM python:3.11-alpine

RUN mkdir /eshop
WORKDIR /eshop

#set environment variable // is an environment variable used to prevent Python from writing bytecode (.pyc) files to disk.
ENV PYTHONDONTWRITEBYCODE 1
ENV PYTHONUNBUFFERED 1

#install pyscopg2 dependencies
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev linux-headers

#install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . /eshop/

EXPOSE 8000

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]