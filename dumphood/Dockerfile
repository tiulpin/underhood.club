FROM node:10.16.3-buster-slim as node-base

COPY package*.json .
RUN npm install
COPY . .
ENTRYPOINT [ "/entrypoint.sh" ]
