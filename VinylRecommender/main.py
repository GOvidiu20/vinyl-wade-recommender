import json

import flask
from flask import request
from flask_cors import CORS

from services.SPARQLService import SPARQLService
from services.processUserData import process_music_preference

app = flask.Flask(__name__)
CORS(app)

sparqlService = SPARQLService()


@app.route('/songs', methods=['POST'])
def get_songs():
    number = request.args.get('number', default=10, type=int)
    user_input = request.json['text']
    processed_results = process_music_preference(user_input)
    result = sparqlService.get_songs(processed_results, number)
    json_string = json.dumps([ob.__dict__ for ob in result.vinylDTOS])
    return json_string


@app.route('/spotify', methods=['POST'])
def spotify():
    data = request.get_json()
    result = sparqlService.spotify(data["artists"], data["genres"])
    json_string = json.dumps([ob.__dict__ for ob in result.vinylDTOS])
    return json_string


if __name__ == '__main__':
    app.run()
