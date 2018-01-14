from flask import Flask

from models import db
from views.question import questions_bp


def read_config(app):
    app.config.from_object('config_dev.Config')
    return app


def register_blueprints(app, prefix="/api"):
    app.register_blueprint(questions_bp, url_prefix=prefix)
    return app


def init_db(app):
    db.init_app(app)


def factory():
    app = Flask(__name__)
    read_config(app)

    init_db(app)
    register_blueprints(app)
    return app


if __name__ == "__main__":
    app = factory()
    app.run(host="0.0.0.0")
