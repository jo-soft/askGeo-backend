from flask import Flask
from models import db

from views.question import questions_bp


def register_blueprints(app):
    app.register_blueprint(questions_bp)
    return app


def factory():
    _app = Flask(__name__)

    db.init_app(_app)

    register_blueprints(_app)
    return _app


if __name__ == "__main__":
    app = factory()
    app.run(host="0.0.0.0", debug=True)
