# blog app in django with graphing capabilities

## django app

### development

To run the django development server on port 8001:

    cd django/site1
    python manage.py runserver 8001

Server will be accessible at localhost:8001

## webserver

### nginx

The following directories are mapped to the nginx default locations:
* nginx to /etc/nginx
* html to /usr/share/nginx/html

To launch nginx alone:

    docker-compose run --service-ports nginx

### nginx serving django applications with uwsgi

Django applications are located in django/, and mounted as /usr/share/django
in the uwsgix image.

First, build the docker image for the uwsgi server:

    cd uwsgi-image
    docker build --network host -t uwsgi .

Then update docker-compose.yml to match the app name in the django path.

Launch docker-compose:

    docker-compose up

Note: it is mandatory to launch everything at once using the up command so that
docker-compose creates the network links between the ports. In this case, the
nginx container may access the uwsgi port using the container port (and not
the host port).
