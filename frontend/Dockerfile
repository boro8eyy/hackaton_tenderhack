# Multi-stage build
FROM node:20-alpine AS builder

WORKDIR /app

# Build argument для API URL
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=${VITE_API_URL}

# Копируем package.json и устанавливаем зависимости
COPY package.json package-lock.json* ./
RUN npm ci

# Копируем исходный код и собираем
COPY . .
RUN npm run build

# Production stage с node adapter
FROM node:20-alpine AS production

WORKDIR /app

# Копируем собранное приложение
COPY --from=builder /app/build ./build
COPY --from=builder /app/package.json ./
COPY --from=builder /app/node_modules ./node_modules

EXPOSE 3000
ENV PORT=3000
ENV HOST=0.0.0.0

CMD ["node", "build"]
