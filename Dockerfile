# pull upstream terraform image
FROM hashicorp/terraform:1.3.3 AS terraform

# it's offical so i'm using it + alpine so damn small
FROM python:3.10.0b2-alpine3.12

# exposing the port
EXPOSE 80

# set python to be unbuffered
ENV PYTHONUNBUFFERED=1

# set terraform automation flag
ENV TF_IN_AUTOMATION=true

# install required packages
RUN apk add --no-cache libffi-dev

# copy terraform binary
COPY --from=terraform /bin/terraform /usr/local/bin/terraform

# adding the gunicorn config
COPY config/config.py /etc/gunicorn/config.py

COPY requirements.txt /www/requirements.txt
RUN pip install -r /www/requirements.txt

# copy the codebase
COPY . /www
RUN chmod +x /www/terraformize_runner.py

# and running it
CMD ["gunicorn" ,"--config", "/etc/gunicorn/config.py", "terraformize_runner:app"]
