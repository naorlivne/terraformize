import os


host = os.getenv("HOST") if os.getenv("HOST") else "0.0.0.0"
port = os.getenv("PORT") if os.getenv("PORT") else "80"
bind = f"{host}:{port}"

worker_class = os.getenv("WORKER_CLASS") if os.getenv("WORKER_CLASS") else "sync"
workers = os.getenv("WORKERS") if os.getenv("WORKERS") else "1"
threads = os.getenv("THREADS") if os.getenv("THREADS") else "1"
preload = os.getenv("PRELOAD") if os.getenv("PRELOAD") else False

chdir = "/www"

loglevel = os.getenv("LOG_LEVEL") if os.getenv("LOG_LEVEL") else "error"
errorlog = "-"
accesslog = "-"
