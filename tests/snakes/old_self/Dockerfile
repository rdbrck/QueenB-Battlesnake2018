FROM python:3.4

RUN mkdir -p /var/www
WORKDIR /var/www
COPY . /var/www
RUN pip3 install -r requirements.txt

ENV PYTHONUNBUFFERED 1
EXPOSE 5000
