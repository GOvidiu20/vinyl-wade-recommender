from rdflib import Graph
from rdflib.plugins.sparql import prepareQuery

from VinylRecommender.services.SPARQLQueryBuilder import SPARQLQueryBuilder


class VinylDTO:
    def __int__(self):
        self.album = None
        self.creator = None
        self.subject = None
        self.date = None
        self.vinylLabel = None
        self.title = None


class VinylDTOS:
    def __init__(self):
        self.vinylDTOS = []


class QueryDTO:
    def __init__(self, query):
        self.query = query


class SPARQLService:
    RDF_FILE_PATH = "VinylRecommender/data/modified_file.ttl"

    def executeQuery(self, queryDTO: QueryDTO) -> VinylDTOS:
        graph = Graph()
        graph.parse(self.RDF_FILE_PATH, format="turtle")
        query = prepareQuery(queryDTO.query)
        vinylDTOS = VinylDTOS()

        for row in graph.query(query):
            vinylDTO = VinylDTO()
            vinylDTO.album = str(row.album)
            vinylDTO.creator = str(row.creator)
            vinylDTO.subject = str(row.subject)
            vinylDTO.date = str(row.date)
            vinylDTO.vinylLabel = str(row.vinylLabel)
            vinylDTO.title = str(row.title)

            vinylDTOS.vinylDTOS.append(vinylDTO)

        return vinylDTOS

    def get_songs(self, limit):
        queryBuilder = SPARQLQueryBuilder("")
        queryBuilder.create_query()
        queryBuilder.end_query()
        queryBuilder.add_limit(limit)
        query_dto = QueryDTO(query=queryBuilder.query)
        result = self.executeQuery(query_dto)
        return result

    def sporify(self, artists, genres):
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