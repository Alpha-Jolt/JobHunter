# Stage 1 — Builder
FROM node:18-alpine AS builder
WORKDIR /build
COPY package*.json ./
COPY shared/ ./shared/
COPY services/auth/ ./services/auth/
RUN npm ci --workspace=shared --workspace=services/auth --include-workspace-root
RUN npm run build --workspace=shared
RUN npm run build --workspace=services/auth

ARG LICENSE_SIGNING_KEY
# argon2 is a native Node.js addon — cannot be bundled by esbuild.
# pino uses worker threads that resolve paths relative to __dirname at runtime —
# bundling it breaks __dirname resolution, so it must also be external.
RUN npx esbuild services/auth/dist/server.js \
    --bundle --minify --platform=node \
    --external:argon2 \
    --external:pino \
    --external:pino-pretty \
    --external:thread-stream \
    --define:__LICENSE_SIGNING_KEY__="\"$LICENSE_SIGNING_KEY\"" \
    --outfile=bundle.js

# Stage 2 — Runtime
# argon2 is a native addon that requires @mapbox/node-pre-gyp and its transitive
# dependencies at runtime to locate its compiled .node binary. Ship node_modules
# in full to satisfy the entire native dependency chain.
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /build/bundle.js ./bundle.js
COPY --from=builder /build/node_modules ./node_modules
EXPOSE 3001
CMD ["node", "bundle.js"]
