from rdflib import Graph
from rdflib.plugins.sparql import prepareQuery
import requests

import xmltodict
from services.SPARQLQueryBuilder import SPARQLQueryBuilder

from google.cloud import storage


class VinylDTO:
    def __int__(self):
        self.creator = None
        self.genre = None
        self.date = None
        self.vinylLabel = None
        self.discogs = None
        self.discogs_image = None


class VinylDTOS:
    def __init__(self):
        self.vinylDTOS = []


class QueryDTO:
    def __init__(self, query):
        self.query = query


class SPARQLService:

    def executeQuery(self, queryDTO: QueryDTO) -> VinylDTOS:

        storage_client = storage.Client()
        bucket = storage_client.get_bucket("vinyl-recommender")
        blob = bucket.blob("music.ttl")

        graph = Graph()
        graph.parse(blob.download_as_string(), format="turtle")

        query = prepareQuery(queryDTO.query)
        vinylDTOS = VinylDTOS()
        for row in graph.query(query):
            vinylDTO = VinylDTO()
            vinylDTO.creator = str(row.creator)
            vinylDTO.genre = str(row.subject)
            vinylDTO.date = str(row.date)
            vinylDTO.vinylLabel = str(row.vinylLabel)
            uri, image = self.fetch_discogs_data(row.creator)
            vinylDTO.discogs = uri
            vinylDTO.discogs_image = image
            vinylDTOS.vinylDTOS.append(vinylDTO)

        return vinylDTOS

    def get_songs(self, user_preferences):
        queryBuilder = SPARQLQueryBuilder("")
        queryBuilder.create_query()
        queryBuilder.add_filters(user_preferences)
        queryBuilder.end_query()
        queryBuilder.add_limit(18)
        query_dto = QueryDTO(query=queryBuilder.query)
        result = self.executeQuery(query_dto)
        return result

    def spotify(self, artists, genres):
        queryBuilder = SPARQLQueryBuilder("")
        queryBuilder.create_query()
        if artists:
            queryBuilder.add_filter_artist(artists)
        if genres:
            queryBuilder.add_filter_genre(genres)
        queryBuilder.end_query()
        queryBuilder.add_limit(18)
        query_dto = QueryDTO(query=queryBuilder.query)
        result = self.executeQuery(query_dto)
        return result

    def document(self, file_content):
        data_dict = xmltodict.parse(file_content)
        track_list = data_dict['playlist']['trackList']['track']
        artists = []
        for track in track_list:
            for artist in track['creator'].split(", "):
                if artist not in artists:
                    artists.append(artist)

        queryBuilder = SPARQLQueryBuilder("")
        queryBuilder.create_query()
        queryBuilder.add_filter_artist(artists)
        queryBuilder.end_query()
        queryBuilder.add_limit(18)
        query_dto = QueryDTO(query=queryBuilder.query)
        result = self.executeQuery(query_dto)
        return result

    def fetch_discogs_data(self, artist_name):
        api_key = "yGrcPrZCSijvHSNdbtsk"
        api_secret = "crhtnFdQcgXMVXYtgzBYJnbBGSWOmSZA"
        discogs_url = f"https://api.discogs.com/database/search?q={artist_name}&key={api_key}&secret={api_secret}"
        response = requests.get(discogs_url)
        data = response.json()
        if 'results' in data and data['results']:
            rs = data['results'][0]
            data2 = "https://www.discogs.com" + rs['uri']
            return data2, rs['cover_image']
        else:
            return None