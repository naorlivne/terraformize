import os
import sys
import logging
from threading import Thread
from terraformize.terraformize_configure import read_configurations
from terraformize.terraformize_endpoint import app
from terraformize.terraformize_queue import RabbitWorker

# Configure the logger to log errors
logging.basicConfig(level=logging.ERROR)

def configure_rabbitmq(configuration):
    rabbit_url = configuration.get("rabbit_url_connection_string")
    if rabbit_url:
        try:
            rabbit_object = RabbitWorker(
                rabbit_url,
                configuration["rabbit_read_queue"],
                configuration["rabbit_reply_queue"]
            )
            thread = Thread(target=rabbit_object.read_from_queue, kwargs={'command': "apply"})
            thread.start()
        except Exception as e:
            logging.error("RabbitMQ related issues - dropping container: %s", e)
            exit(2)
#added error handling
def main():
    try:
        configuration = read_configurations(os.getenv("CONFIG_DIR", "config"))
    except Exception as e:
        logging.error("Error while reading configurations - dropping container: %s", e)
        exit(2)

    configure_rabbitmq(configuration)

    try:
        app.run(host="127.0.0.1", port=5000, threaded=True)
    except Exception as e:
        logging.error("Flask connection failure - dropping container: %s", e)
        exit(2)

if __name__ == "__main__":
    main()
