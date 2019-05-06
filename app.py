import os
from flask import Flask
from api.AuthorizationAPI import auth_api
from api.UserAPI import user_api
from api.ListAPI import list_api
from api.SearchAPI import search_api
from api.FavoriteAPI import favorite_api
from api.FilterAPI import filter_api
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.register_blueprint(user_api, url_prefix='/user')
app.register_blueprint(auth_api, url_prefix='/auth')
app.register_blueprint(list_api, url_prefix='/list')
app.register_blueprint(search_api, url_prefix='/search')
app.register_blueprint(favorite_api, url_prefix='/favorite')
app.register_blueprint(filter_api, url_prefix='/filter')


@app.route("/", methods=['GET'])
def helloWorld():
    return "Welcome to the Hunter Barterplace API. There's nothing to see here."


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, threaded=True, debug=True)
