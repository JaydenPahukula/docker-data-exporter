import flask
from flask_cors import CORS, cross_origin
import os
import sys
import threading
import yaml

from methods.scrape import scraper
from methods.handle_query import handle_query

SCRAPE_INTERVAL = 600 # (seconds)
IP_LIST = []
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

app = flask.Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/', methods=["GET"])
@cross_origin()
def root():
    return "OK"

@app.route('/search', methods=["POST"])
@cross_origin()
def search():
    return '["total-container-count","running-container-count","option3"]'

@app.route('/query', methods=["POST"])
@cross_origin()
def query():
    return handle_query(flask.request.json)

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