from terraformize.terraformize_endpoint import *


if __name__ == "__main__":
    try:
        app.run(host="127.0.0.1", port=5000, threaded=True)
    except Exception as e:
        print("Flask connection failure - dropping container")
        print(e, file=sys.stderr)
        exit(2)
