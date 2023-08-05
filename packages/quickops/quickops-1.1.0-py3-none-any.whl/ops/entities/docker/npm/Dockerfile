FROM node:18-alpine
ENV NODE_ENV=$NODE_ENV

WORKDIR /app

COPY ["package.json", "package-lock.json*", "./"]

RUN npm install --$NODE_ENV

COPY . .

CMD ["node", "server.js"]
