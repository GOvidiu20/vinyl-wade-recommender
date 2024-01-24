import csv

from rdflib import Graph, Literal, Namespace, RDF, XSD
from urllib.parse import quote

ex = Namespace("http://example.org/")
dct = Namespace("http://purl.org/dc/terms/")
schema = Namespace("https://schema.org/")

graph = Graph()


csv_file_path = '../data/query.csv'

with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
    csv_reader = csv.DictReader(csvfile)

    for row in csv_reader:
        album_uri = ex[quote(row['albumLabel'].replace(' ', '_'))]

        graph.add((album_uri, RDF.type, schema.MusicRecording))
        graph.add((album_uri, schema.name, Literal(row['albumLabel'])))
        graph.add((album_uri, schema.byArtist, Literal(row['artistLabel'])))
        graph.add((album_uri, schema.genre, Literal(row['genreLabel'])))
        graph.add((album_uri, schema.datePublished, Literal(row['date'], datatype=XSD.date)))
        graph.add((album_uri, ex.vinylLabel, Literal(row['vinylLabel'])))

ttl_data = graph.serialize(format='turtle')

ttl_file_path = '../data/outputt.ttl'
with open(ttl_file_path, 'w', encoding='utf-8') as ttlfile:
    ttlfile.write(ttl_data)

print(f'TTL data has been saved to {ttl_file_path}')
