from flask import Flask

from models import db
from views.answerView import answer_bp
from views.questionView import questions_bp


def read_config(app, config_path='config_dev.Config'):
    app.config.from_object(config_path)
    return app


def register_blueprints(app, prefix="/api"):
    app.register_blueprint(questions_bp, url_prefix=prefix)
    app.register_blueprint(answer_bp, url_prefix=prefix)
    return app


def init_db(app):
    db.init_app(app)


def factory(config_path=None):
    app = Flask(__name__)
    read_config(app, config_path)

    init_db(app)
    register_blueprints(app)
    return app


if __name__ == "__main__":
    app = factory()
    app.run(host="0.0.0.0")
