import flask
import sys


app = flask.Flask(__name__)


@app.route('/', methods=["GET", "OPTIONS"])
def root():
  return "OK"




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