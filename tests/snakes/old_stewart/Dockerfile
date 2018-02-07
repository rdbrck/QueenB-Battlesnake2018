FROM node:8

RUN mkdir -p /home/node/app
WORKDIR /home/node/app
COPY . /home/node/app
RUN npm install
EXPOSE 7000

CMD ["node", "."]
