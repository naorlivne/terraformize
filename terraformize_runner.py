# Python script that sets up an API endpoint using Flask and incorporates some additional functionality related to RabbitMQ (a message queue system) for handling asynchronous tasks

from terraformize.terraformize_endpoint import *
from threading import Thread
from terraformize.terraformize_queue import *
from terraformize.terraformize_configure import *

# if RabbitMQ is configured opens a new thread to read from queue too, reason for new thread is not to block the API
# endpoint so to allow the health checks to carry on working
if configuration["rabbit_url_connection_string"] is not None:
    try:
        configuration = read_configurations(os.getenv("CONFIG_DIR", "config"))
        rabbit_object = RabbitWorker(configuration["rabbit_url_connection_string"], configuration["rabbit_read_queue"],
                                     configuration["rabbit_reply_queue"])
        thread = Thread(target=rabbit_object.read_from_queue(), kwargs={'command': "apply"})
        thread.start()
    except Exception as e:
        print("RabbitMQ related issues - dropping container")
        print(e, file=sys.stderr)
        exit(2)

# this is used form testing only, will usually run using a containerized gunicorn server
if __name__ == "__main__":
    try:
        app.run(host="127.0.0.1", port=5000, threaded=True)
    except Exception as e:
        print("Flask connection failure - dropping container")
        print(e, file=sys.stderr)
        exit(2)
