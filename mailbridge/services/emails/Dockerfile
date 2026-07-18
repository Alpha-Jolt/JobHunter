# Stage 1 — Builder
FROM node:18-alpine AS builder
WORKDIR /build
COPY package*.json ./
COPY shared/ ./shared/
COPY services/emails/ ./services/emails/
RUN npm ci --workspace=shared --workspace=services/emails --include-workspace-root
RUN npm run build --workspace=shared
RUN npm run build --workspace=services/emails

ARG LICENSE_SIGNING_KEY
RUN npx esbuild services/emails/dist/server.js \
    --bundle --minify --platform=node \
    --define:__LICENSE_SIGNING_KEY__="\"$LICENSE_SIGNING_KEY\"" \
    --outfile=bundle.js

# Stage 2 — Runtime (no source, no node_modules)
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /build/bundle.js ./bundle.js
EXPOSE 3003
CMD ["node", "bundle.js"]
