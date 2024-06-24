print("start http...")

from flask import (
    Flask,
    render_template,
    Response,
    redirect,
    url_for,
    make_response,
)
from flask_cors import CORS
import numpy as np
import logging

# ============================================== #
from src.http_server import get_handler, post_handler
# from src import CLI
# from src.CLI import Level

print_name = "FLASK"



#
log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

#
# app = Flask(__name__, static_url_path="/src/http_server/static")  # flask app
app = Flask(__name__, static_folder='static', static_url_path='/static')

CORS(app)
# app.register_blueprint(get_handler.blueprint)
app.register_blueprint(post_handler.blueprint)


@app.route("/")
def index():
    return render_template(
        "index.html"
    )

# ============================================== #
def start(host="0.0.0.0", port=8080):
    print( "({:^10}) Started Server.".format(print_name))
    app.run(host=host, port=port)


print("end http...")

if __name__ == "__main__":
    start()



