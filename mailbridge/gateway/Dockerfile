FROM nginx:1.25-alpine
COPY nginx.conf /etc/nginx/nginx.conf
RUN rm -f /etc/nginx/conf.d/default.conf
EXPOSE 3009
CMD ["nginx", "-g", "daemon off;"]
