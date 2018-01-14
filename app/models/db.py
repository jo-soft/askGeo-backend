from flask_pymongo import PyMongo

mongo = None


def _init_db_(app):
    global mongo
    mongo = PyMongo(app)


def init_app(app):
    _init_db_(app)
    return app


def get_db():
    return mongo.db
