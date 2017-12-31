from flask_pymongo import PyMongo


def init_app(app):
    mongo = PyMongo(app)
    return mongo
