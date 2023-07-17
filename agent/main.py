import flask
import sys

from methods.subprocess_run import subprocessRun

app = flask.Flask(__name__)


@app.route('/')
def root():
  return "OK"

@app.route('/get-data')
def getData():
  output = {}

  # getting container count
  completed_command = subprocessRun("docker ps -a --format {{.Names}}")
  container_count = completed_command.stdout.decode().count("\n")
  output.update({"total-container-count": container_count})

  # getting running container count
  completed_command = subprocessRun("docker ps --format {{.Names}}")
  running_container_count = completed_command.stdout.decode().count("\n")
  output.update({"running-container-count": running_container_count})

  return flask.make_response(output, 200)



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