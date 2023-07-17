import flask
from flask_cors import CORS, cross_origin

import sys


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
  return '["option1","option2","option3"]'



if __name__ == '__main__':
  print("\n\n\n")

  port = 5000 # default port
  # getting port argument
  for i in range(len(sys.argv)):
    if (sys.argv[i] == "-p" or sys.argv[i] == "-port") and i + 1 < len(sys.argv):
      try:
        port = int(sys.argv[i + 1])
      except ValueError:
        pass
      finally:
        break

  app.run(port=port)