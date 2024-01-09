import chardet as chardet
from rdflib import Graph

file_path = '../data/modified_file.ttl'


g = Graph()
g.parse(file_path, format="turtle")

query = """
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX ns1: <http://example.org/>
SELECT DISTINCT ?artist
WHERE {
    ?s a ns1:Album ;
       dcterms:creator ?artist .
}
"""

results_artists = g.query(query)

distinct_artists = [str(row.artist) for row in results_artists]
print(distinct_artists)

