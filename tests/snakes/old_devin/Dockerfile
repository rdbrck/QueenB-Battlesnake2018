FROM python:2.7

RUN mkdir -p /var/www
WORKDIR /var/www
COPY . /var/www
RUN pip install -r requirements.txt

ENV PYTHONUNBUFFERED 1
EXPOSE 6000
