# nginx in docker

## Basic webserver

The following directories are mapped to the nginx default locations:
* nginx to /etc/nginx
* html to /usr/share/nginx/html

Launch with `docker-compose run --service-ports nginx`

## With django applications

Django applications are located in django/, and mounted as /usr/share/django
in the uwsgix image.

First, build the docker image for the uwsgi server:
    cd uwsgi-image
    docker build -t uwsgi .

Then update docker-compose.yml to match the app name in the django path.

Launch docker-compose:
    docker-compose up

Note: it is mandatory to launch everything at once using the up command so that
docker-compose creates the network links between the ports. In this case, the
nginx container may access the uwsgi port using the container port (and not
the host port).
