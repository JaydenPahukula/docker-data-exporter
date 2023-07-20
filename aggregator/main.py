import flask
import os
import sys
import threading
import yaml

from aggregator.methods.scraper import scraper
from methods.handle_query import handle_query, get_hostnames

SCRAPE_INTERVAL = 60 # seconds (default)
IP_LIST = []
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

app = flask.Flask(__name__)


@app.route('/', methods=["GET"])
def root():
    return "OK"

@app.route('/search', methods=["POST"])
def search():
    if flask.request.json["target"] == "hostname":
        return get_hostnames()
    return '["hostname","docker-running","docker-version","swarm-mode","image-count","total-container-count","running-container-count"]'

@app.route('/query', methods=["POST"])
def query():
    return handle_query(flask.request.json)

@app.route('/tag-keys', methods=["POST"])
def tagkeys():
    return flask.jsonify({"type":"string", "text":"hostname"})

@app.route('/tag-values', methods=["POST"])
def tagvals():
    if flask.request.json["key"] != "hostname":
        return "invalid key"
    return flask.jsonify({"text":hostname for hostname in get_hostnames()})

if __name__ == '__main__':
    print("\n\n\n")
    
    print(" * Reading config file")
    with open(CURRENT_DIR + "/config.yaml", "r") as config_file:
        config = yaml.safe_load(config_file)

    SCRAPE_INTERVAL = config["scrape-interval"]
    IP_LIST = config["server-ips"]

    print(" * Starting scraper thread")
    scraper_thread = threading.Thread(target=scraper, args=(IP_LIST, SCRAPE_INTERVAL), daemon=True)
    scraper_thread.start()

    port = 5000 # default port
    # getting port argument
    for i in range(len(sys.argv)):
        if (sys.argv[i] == "-p" or sys.argv[i] == "-port") and i + 1 < len(sys.argv):
            try:
                port = int(sys.argv[i + 1])
            except ValueError:
                pass
            break

    app.run(port=port)