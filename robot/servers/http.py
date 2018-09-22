from flask import Flask, request
from flask_restful import Resource, Api
from flask.ext.jsonify import jsonify


app = Flask(__name__)
api = Api(app)


def run_server(driver):
    app.run(port=5432)
