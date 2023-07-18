import flask
from flask_cors import CORS, cross_origin
import sys
import threading

from methods.scrape import scraper
from methods.handle_query import handle_query

SCRAPEINTERVAL = 60 # seconds
IPLIST = ["127.0.0.1:5001"]

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

    print(" * Starting scraper thread")
    logThread = threading.Thread(target=scraper, args=(IPLIST, SCRAPEINTERVAL), daemon=True)
    logThread.start()

    port = 5000 # default port
    # getting port argument
    for i in range(len(sys.argv)):
        if (sys.argv[i] == "-p" or sys.argv[i] == "-port") and i + 1 < len(sys.argv):
            try:                port = int(sys.argv[i + 1])
            except ValueError:  pass
            finally:            break

    app.run(port=port)