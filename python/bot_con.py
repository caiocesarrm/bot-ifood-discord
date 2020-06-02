from flask import Flask, jsonify, request
import json
from options import pipeline

app = Flask(__name__)

@app.route("/")
def test():
    res = {'success':True}
    return jsonify(res)

@app.route("/ifood/", methods = ['POST'])
def ifood():
    data = request.json
    res = pipeline(data['palavras_chave'], data['nota_minima'], data['lat'], data['long'])
    return jsonify(res)


app.run()