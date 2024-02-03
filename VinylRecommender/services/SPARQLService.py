from stardog import Connection
import requests

import xmltodict
from services.SPARQLQueryBuilder import SPARQLQueryBuilder


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
    conn_details = {
        'endpoint': 'https://sd-a3138be8.stardog.cloud:5820/vire/query',
        'username': 'stratianub45@gmail.com',
        'password': 'RbWWZPsSwk9U29N'
    }

    def executeQuery(self, queryDTO: QueryDTO) -> VinylDTOS:

        conn = Connection('vire', endpoint='https://sd-a3138be8.stardog.cloud:5820',
                          username='stratianub45@gmail.com', password='RbWWZPsSwk9U29N')
        result = conn.select(queryDTO.query)
        print(result)
        vinylDTOS = VinylDTOS()
        for row in result['results']['bindings']:
            vinylDTO = VinylDTO()
            vinylDTO.creator = str(row['creator']['value'])
            vinylDTO.genre = str(row['subject']['value'])
            vinylDTO.date = str(row['date']['value'])
            vinylDTO.vinylLabel = str(row['vinylLabel']['value'])
            uri, image = self.fetch_discogs_data(row['creator']['value'])
            if uri and image:
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
            return None, None