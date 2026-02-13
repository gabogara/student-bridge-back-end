from flask import Flask
from flask_cors import CORS

from blueprints.auth_blueprint import authentication_blueprint
from blueprints.resources_blueprints import resources_blueprint
from blueprints.verifications_blueprint import verifications_blueprint
from blueprints.users_blueprint import users_blueprint

app = Flask(__name__)
CORS(app)
app.register_blueprint(authentication_blueprint)
app.register_blueprint(users_blueprint)
app.register_blueprint(resources_blueprint)
app.register_blueprint(verifications_blueprint)


@app.route('/')
def index():
    return "Hello world"

if __name__ == '__main__':
    app.run()

