
class SPARQLQueryBuilder:
    def __init__(self, query):
        self.query = query

    def create_query(self):
        self.query = (
            "PREFIX dcterms: <http://purl.org/dc/terms/>\n"
            "PREFIX ns1: <http://example.org/>\n"
            "PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>\n"
            "SELECT ?album ?vinylLabel ?creator ?date ?subject ?title\n"
            "WHERE {\n"
            "  ?album a ns1:Album ;\n"
            "         ns1:vinylLabel ?vinylLabel ;\n"
            "         dcterms:creator ?creator ;\n"
            "         dcterms:date ?date ;\n"
            "         dcterms:subject ?subject ;\n"
            "         dcterms:title ?title .\n"
        )

    def add_filter_date(self, operator, date_range):
        operators_mapping = {
            "after": ">",
            "before": "<",
            "to": "=",
            "from": "=",
            "between": ">=",
        }

        if operator in operators_mapping:
            if operator == "between" and len(date_range) == 2:
                self.query += f"  FILTER(YEAR(?date) {operators_mapping[operator]} {date_range[0]} && YEAR(?date) {operators_mapping['before']} {date_range[1]})\n"
            else:
                self.query += f"  FILTER(YEAR(?date) {operators_mapping[operator]} {date_range[0]})\n"
        else:
            raise ValueError("Invalid date filter operator")

    def add_filter_artist(self, artists_names):
        if not artists_names:
            raise ValueError("No artist names provided")

        artist_filters = " || ".join([f'CONTAINS(LCASE(?creator), LCASE("{artist}"))' for artist in artists_names])
        self.query += f'  FILTER({artist_filters})\n'

    def add_filter_not_artist(self, artist_names):
        if not artist_names:
            raise ValueError("No artist names provided")

        artist_filters = " || ".join([f'CONTAINS(?creator, "{artist}")' for artist in artist_names])
        self.query += f'  FILTER NOT EXISTS {{ ?album dcterms:creator ?creator .\n'
        self.query += f'                     FILTER({artist_filters}) }}\n'

    def add_filter_not_contains_genre(self, genre_names):
        if not genre_names:
            raise ValueError("No genre names provided")

        genre_filters = " || ".join([f'CONTAINS(?subject, "{genre}")' for genre in genre_names])
        self.query += f'  FILTER NOT EXISTS {{ ?album dcterms:subject ?genreValue .\n'
        self.query += f'                   FILTER({genre_filters}) }}\n'

    def add_filter_genre(self, genres_names):
        if not genres_names:
            raise ValueError("No genre names provided")

        genre_filters = " || ".join([f'CONTAINS(?subject, "{genre}")' for genre in genres_names])
        self.query += f'  FILTER({genre_filters})\n'

    def add_filter_album(self, album_names):
        if not album_names:
            raise ValueError("No album names provided")
        album_filters = " || ".join([f'CONTAINS(?vinylLabel, "{album}")' for album in album_names])
        self.query += f'  FILTER({album_filters})\n'

    def add_limit(self, limit_value):
        if not isinstance(limit_value, int) or limit_value <= 0:
            raise ValueError("Invalid limit value. Limit must be a positive integer.")

        self.query += f"  LIMIT {limit_value}\n"

    def end_query(self):
        self.query = self.query + "}"

    def delete_query(self):
        self.query = ""
