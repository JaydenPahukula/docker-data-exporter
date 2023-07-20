from flask import Flask
import os
import sys
import yaml

# import methods.scraper

IP_LIST = []
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
#app.wsgi_app = DispatcherMiddleware(app.wsgi_app, { '/metrics': make_wsgi_app() })
@app.route('/metrics')
def root():
    return "test_metric_1{hostname=\"examplehostname\"} 5\ntest_metric_1{hostname=\"hello\"} 7"

if __name__ == '__main__':
    print("\n\n\n")
    
    print(" * Reading config file")
    with open(CURRENT_DIR + "/aggregator_config.yaml", "r") as config_file:
        config = yaml.safe_load(config_file)
    IP_LIST = config["server-ips"]

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