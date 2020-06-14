# nginx in docker

## Basic webserver

The following directories are mapped to the nginx default locations:
* nginx to /etc/nginx
* html to /usr/share/nginx/html

Launch with `docker-compose run --service-ports nginx`
