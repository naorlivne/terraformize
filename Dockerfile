# pull upstream terraform image
FROM hashicorp/terraform:light AS terraform

# it's offical so i'm using it + alpine so damn small
FROM python:3.7.4-alpine3.10

# exposing the port
EXPOSE 80

# set python to be unbuffered
ENV PYTHONUNBUFFERED=1

# set tearrform automation flag
ENV TF_IN_AUTOMATION=true

# install required packages - requires build-base due to gevent GCC compiler requirements
RUN apk add --no-cache \
	build-base \
	libffi-dev

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
