import json
import flask
from flask import request
from flask_cors import CORS, cross_origin

from services.SPARQLService import SPARQLService
from services.processUserData import process_music_preference

app = flask.Flask(__name__)
CORS(app)

sparqlService = SPARQLService()


@app.route('/songs', methods=['POST'])
def get_songs():
    user_input = request.json['text']
    processed_results = process_music_preference(user_input)
    result = sparqlService.get_songs(processed_results)
    json_string = json.dumps([ob.__dict__ for ob in result.vinylDTOS])

    return json_string


@app.route('/spotify', methods=['POST'])
@cross_origin()
def spotify():
    data = request.get_json()
    result = sparqlService.spotify(data["artists"], data["genres"])
    json_string = json.dumps([ob.__dict__ for ob in result.vinylDTOS])

    return json_string


@app.route('/document', methods=['POST'])
@cross_origin()
def addDocument():
    file = request.files.get("file")
    file_content = file.read()
    result = sparqlService.document(file_content)
    json_string = json.dumps([ob.__dict__ for ob in result.vinylDTOS])

    return json_string


if __name__ == '__main__':
    app.run()
