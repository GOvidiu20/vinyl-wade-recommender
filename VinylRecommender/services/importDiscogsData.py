from rdflib import Graph, Namespace, Literal, RDF

import discogs_client

# Define namespaces
mo = Namespace("http://purl.org/ontology/mo/")
dc = Namespace("http://purl.org/dc/elements/1.1/")
foaf = Namespace("http://xmlns.com/foaf/0.1/")


def get_all_vinyl_releases():
    discogs = discogs_client.Client('YourApp/1.0', user_token='BPxkDcXJltGSHDXcPfdgbeSYMcuNqebfOXlxzziB')
    artists = []
    genres = []
    page = 0
    ids = []
    while True:
        page += 1

        try:
            releases = discogs.search(type='release')

            for release in releases:
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
                            if artist.name not in artists:
                                artists.append(artist.name)
                                with open('../data1/artists.txt', 'a', encoding='utf-8') as filehandle:
                                    filehandle.write(f'{artist.name}\n')

                            g.add((release_uri, foaf['name'], Literal(artist.name)))

                        for genre in track.genres:
                            genre = genre.lower()
                            if genre not in genres:
                                genres.append(genre)
                                with open('../data1/genres.txt', 'a', encoding='utf-8') as filehandle:
                                    filehandle.write(f'{genre}\n')

                            g.add((release_uri, mo['genre'], Literal(genre)))

                        ttl_data = g.serialize(format='turtle')
                        # Append TTL data to the file
                        with open('../data1/music.ttl', 'a') as ttl_file:
                            ttl_file.write(ttl_data)
                except UnicodeEncodeError as e:
                    continue

        except discogs_client.exceptions.HTTPError as e:
            continue


# Example usage
if __name__ == "__main__":
    get_all_vinyl_releases()
