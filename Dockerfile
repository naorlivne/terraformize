# it's offical so i'm using it + alpine so damn small
FROM python:3.7.4-alpine3.10

# copy the codebase
COPY . /www
RUN chmod +x /www/terraformize_runner.py

# make the terraform binary is executable
RUN chmod +x /www/bin/terraform

# symlink the terraform binary to a location on the PATH
RUN ln -s /www/bin/terraform /usr/bin/terraform

# install required packages - requires build-base due to gevent GCC complier requirements
RUN apk add --no-cache build-base libffi-dev
RUN pip install -r /www/requirements.txt

# adding the gunicorn config
COPY config/config.py /etc/gunicorn/config.py

#set python to be unbuffered
ENV PYTHONUNBUFFERED=1

#exposing the port
EXPOSE 80

# and running it
CMD ["gunicorn" ,"--config", "/etc/gunicorn/config.py", "terraformize_runner:app"]
