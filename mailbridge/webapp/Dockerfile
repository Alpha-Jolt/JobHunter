FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
# Subpath on app.myjobhunter.in/mailbridge — MUST be present at build time (inlined into client JS)
ARG NEXT_PUBLIC_BASE_PATH=/mailbridge
ENV NEXT_PUBLIC_BASE_PATH=$NEXT_PUBLIC_BASE_PATH
# Bust stale caches when basePath wiring changes
RUN echo "basePath=${NEXT_PUBLIC_BASE_PATH}" > /tmp/basepath.stamp && npm run build

FROM node:18-alpine
WORKDIR /app
ENV NODE_ENV=production PORT=3010
ARG NEXT_PUBLIC_BASE_PATH=/mailbridge
ENV NEXT_PUBLIC_BASE_PATH=$NEXT_PUBLIC_BASE_PATH
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
EXPOSE 3010
CMD ["node", "server.js"]
