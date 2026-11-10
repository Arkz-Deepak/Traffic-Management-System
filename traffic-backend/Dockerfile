FROM node:20-alpine

WORKDIR /app

# Copy dependency definitions
COPY package*.json ./
RUN npm install --omit=dev

# Copy server code
COPY server.js ./
COPY RosLib.js ./

EXPOSE 3000

ENV PORT=3000

CMD ["node", "server.js"]
