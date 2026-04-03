# ---- Build stage ----
FROM node:18-alpine AS builder
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --silent

COPY . .
ARG REACT_APP_API_URL="/api"
ENV REACT_APP_API_URL=${REACT_APP_API_URL}
RUN npm run build

# ---- Runtime stage ----
FROM nginx:stable-alpine

# apply latest Alpine security patches in the image (zlib/libexpat CVEs)
RUN apk upgrade --no-cache

# create cache dir and set ownership to nginx user (101)
RUN mkdir -p /var/cache/nginx/client_temp \
    && chown -R 101:101 /var/cache/nginx

# copy built static files
COPY --from=builder /app/build /usr/share/nginx/html

# copy custom nginx config (must be present in build context)
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY nginx-main.conf /etc/nginx/nginx.conf

EXPOSE 8080
ENTRYPOINT ["nginx"]
CMD ["-g", "daemon off;"]