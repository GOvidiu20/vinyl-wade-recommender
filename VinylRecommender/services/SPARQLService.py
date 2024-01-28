from rdflib import Graph
from rdflib.plugins.sparql import prepareQuery
import requests

from services.SPARQLQueryBuilder import SPARQLQueryBuilder

from google.cloud import storage


class VinylDTO:
    def __int__(self):
        self.album = None
        self.creator = None
        self.genre = None
        self.date = None
        self.vinylLabel = None
        self.title = None
        self.discogs = None
        self.discogs_image = None


class VinylDTOS:
    def __init__(self):
        self.vinylDTOS = []


class QueryDTO:
    def __init__(self, query):
        self.query = query


class SPARQLService:
    # RDF_FILE_PATH = "VinylRecommender/data/modified_file.ttl"

    def executeQuery(self, queryDTO: QueryDTO) -> VinylDTOS:

        storage_client = storage.Client()
        bucket = storage_client.get_bucket("turtle_file")
        blob = bucket.blob("modified_file.ttl")

        graph = Graph()
        graph.parse(blob.download_as_string(), format="turtle")
        # graph.parse(self.RDF_FILE_PATH, format="turtle")
        query = prepareQuery(queryDTO.query)
        vinylDTOS = VinylDTOS()
        for row in graph.query(query):
            vinylDTO = VinylDTO()
            vinylDTO.album = str(row.album)
            vinylDTO.creator = str(row.creator)
            vinylDTO.genre = str(row.subject)
            vinylDTO.date = str(row.date)
            vinylDTO.vinylLabel = str(row.vinylLabel)
            vinylDTO.title = str(row.title)
            uri, image = self.fetch_discogs_data(row.creator)
            vinylDTO.discogs = uri
            vinylDTO.discogs_image = image
            vinylDTOS.vinylDTOS.append(vinylDTO)

        return vinylDTOS

    def get_songs(self, user_preferences, limit):
        queryBuilder = SPARQLQueryBuilder("")
        queryBuilder.create_query()
        queryBuilder.add_filters(user_preferences)
        queryBuilder.end_query()
        queryBuilder.add_limit(limit)
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
        queryBuilder.add_limit(20)
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


# if __name__ == "__main__":
#     sparql_service = SPARQLService()
#     queryBuilder = SPARQLQueryBuilder("")
#     queryBuilder.create_query()
#     # queryBuilder.add_filter_date("between", ["1973", "1999"])
#
#     # queryBuilder.add_filter_artist(["Sonny", "Stan"])
#     # queryBuilder.add_filter_genre(["pop", "rock"])
#     # queryBuilder.add_filter_not_contains_genre(["pop rock", "rock music"])
#     # queryBuilder.add_filter_not_artist(["Sonny", "Stan"])
#     # queryBuilder.add_filter_album(["Hammer to Fall", "Who's Missing"])
#     queryBuilder.end_query()
#     queryBuilder.add_limit(15)
#
#     query_dto = QueryDTO(query=queryBuilder.query)
#     print(queryBuilder.query)
#
#     result = sparql_service.executeQuery(query_dto)
#
#     for vinyl_dto in result.vinylDTOS:
#         print("Album:", vinyl_dto.album)
#         print("Creator:", vinyl_dto.creator)
#         print("Subject:", vinyl_dto.subject)
#         print("Date:", vinyl_dto.date)
#         print("Vinyl Label:", vinyl_dto.vinylLabel)
#         print("Title:", vinyl_dto.title)
#         print()