import os


host = os.getenv("HOST", "0.0.0.0")
port = os.getenv("PORT", "80")
bind = f"{host}:{port}"

worker_class = os.getenv("WORKER_CLASS", "sync")
workers = os.getenv("WORKERS", "1")
threads = os.getenv("THREADS", "1")
preload = os.getenv("PRELOAD", False)

chdir = "/www"

loglevel = os.getenv("LOG_LEVEL", "error")
errorlog = "-"
accesslog = "-"
