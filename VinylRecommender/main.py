import json
import xmltodict
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


@app.route('/document', methods=['POST'])
def addDocument():
    file = request.files.get("file")
    file_content = file.read()
    data_dict = xmltodict.parse(file_content)
    track_list = data_dict['playlist']['trackList']['track']
    title_from_track = "like music performed by "
    for i in track_list:
        title_from_track += i['title']+" . "+"like "
    title_from_track = title_from_track[:len(title_from_track)-6]
    processed_results = process_music_preference(title_from_track)
    result = sparqlService.get_songs(processed_results, 10)
    json_string = json.dumps([ob.__dict__ for ob in result.vinylDTOS])
    return json_string


if __name__ == '__main__':
    app.run()
