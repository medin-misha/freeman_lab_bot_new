FROM node:22.13-bookworm-slim AS builder

ARG VITE_API_URL=/api
ENV VITE_API_URL=${VITE_API_URL}

WORKDIR /app

RUN npm install -g pnpm@11.1.2

COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY . .
RUN pnpm build

FROM nginx:1.27-alpine

# Copy to the /admin subdirectory to match Caddy routing path /admin
COPY --from=builder /app/dist /usr/share/nginx/html/admin

EXPOSE 80
