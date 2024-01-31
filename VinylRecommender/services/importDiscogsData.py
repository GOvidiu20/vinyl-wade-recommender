import requests
from rdflib import Graph, Namespace, Literal, URIRef, RDF
import time

# Define namespaces
mo = Namespace("http://purl.org/ontology/mo/")
dc = Namespace("http://purl.org/dc/elements/1.1/")
xsd = Namespace("http://www.w3.org/2001/XMLSchema#")
tl = Namespace("http://purl.org/NET/c4dm/timeline.owl#")
event = Namespace("http://purl.org/NET/c4dm/event.owl#")
foaf = Namespace("http://xmlns.com/foaf/0.1/")
rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")


def get_discogs_data(release_id):
    discogs_url = f"https://api.discogs.com/releases/{release_id}"
    response = requests.get(discogs_url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching Discogs data for release {release_id}")
        return None


# Function to create RDF triples from Discogs data
def create_rdf_from_discogs(data):
    g = Graph()

    # Create a unique URI for the release
    release_uri = mo[str(data['id'])]

    # Add triples for basic release information
    g.add((release_uri, mo['title'], Literal(data['title'])))
    g.add((release_uri, dc['date'], Literal(data['released'])))

    # Add triples for artists
    for artist in data['artists']:
        artist_uri = mo[artist['id']]
        g.add((release_uri, mo['performer'], artist_uri))
        g.add((artist_uri, mo['name'], Literal(artist['name'])))

    # Add more triples as needed based on the Music Ontology

    return g


# Example usage
# if __name__ == "__main__":
#     for release_id in [249504]:
#         time.sleep(1)
#         discogs_data = get_discogs_data(release_id)
#         print(discogs_data)
#         if discogs_data:
#             rdf_graph = create_rdf_from_discogs(discogs_data)
#
#             ttl_data = rdf_graph.serialize(format='turtle')
#             # Append TTL data to the file
#             with open('../data/music.ttl', 'a') as ttl_file:
#                 ttl_file.write(ttl_data)

import discogs_client


def get_all_vinyl_releases():
    discogs = discogs_client.Client('YourApp/1.0', user_token='BPxkDcXJltGSHDXcPfdgbeSYMcuNqebfOXlxzziB')

    page = 0
    ids = []
    while True:
        page += 1

        try:
            releases = discogs.search(type='release')
            print(f"Processing page {page}")

            for release in releases:
                print(release)
                if release.id not in [5672557, 13302965, 1758081, 28500334, 28860919, 26059594, 7490374, 16150880]:
                    try:
                        track = discogs.release(release.id)

                        if track.title and track.artists and track.year and track.genres and track.id not in ids:
                            ids.append(track.id)
                            g = Graph()
                            # Create a unique URI for the release
                            release_uri = mo["#track-" + str(track.id)]

                            # Add triples for basic release information
                            g.add((release_uri, RDF.type, mo.Track))
                            g.add((release_uri, dc['title'], Literal(track.title)))
                            g.add((release_uri, dc['date'], Literal(track.year)))

                            # Add triples for artists
                            for artist in track.artists:
                                g.add((release_uri, foaf['name'], Literal(artist.name)))

                            for genre in track.genres:
                                g.add((release_uri, mo['genre'], Literal(genre)))

                            ttl_data = g.serialize(format='turtle')
                            # Append TTL data to the file
                            with open('../data/music.ttl', 'a') as ttl_file:
                                ttl_file.write(ttl_data)
                    except UnicodeEncodeError as e:
                        continue

        except discogs_client.exceptions.HTTPError as e:
            continue


# Example usage
if __name__ == "__main__":
    get_all_vinyl_releases()
