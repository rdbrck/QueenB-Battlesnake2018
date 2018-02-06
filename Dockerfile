FROM python:3.4

RUN mkdir -p /var/www
WORKDIR /var/www
COPY . /var/www
RUN pip3 install -r requirements.txt

ENV PYTHONUNBUFFERED 1
EXPOSE 8080
# CMD ["uwsgi", "uwsgi/battlesnake.ini", "--protocol=http"] - Not sure how we want to deploy this so leaving as comment (would need to add uwsgi as well)
