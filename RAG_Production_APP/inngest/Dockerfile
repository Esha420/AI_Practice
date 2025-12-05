FROM node:20

WORKDIR /app

RUN npm install -g inngest-cli@latest

CMD ["inngest", "dev", "-u", "http://backend:8000/api/inngest", "--no-discovery"]
