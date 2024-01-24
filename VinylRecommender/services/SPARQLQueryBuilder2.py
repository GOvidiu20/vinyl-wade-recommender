class SPARQLQueryBuilder:
    def __init__(self, query):
        self.query = query

    def create_query(self):
        self.query = (
            "PREFIX ns1: <http://example.org/>\n"
            "PREFIX schema: <https://schema.org/>\n"
            "PREFIX dcterms: <http://purl.org/dc/terms/>\n"
            "SELECT ?album ?vinylLabel ?creator ?date ?subject ?title \n"
            "WHERE {\n"
            "  ?album a schema:MusicRecording ;\n"
            "         ns1:vinylLabel ?vinylLabel ;\n"
            "         schema:byArtist ?creator ;\n"
            "         schema:genre ?subject ;\n"
            "         schema:datePublished ?date ;\n"
            "         schema:name ?title .\n"
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
                self.query += f"  FILTER(YEAR(?date) {operators_mapping[operator]} {date_range[0]} && YEAR(?date) {operators_mapping['before']} {date_range[1]})"
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

        artist_filters = " || ".join([f'CONTAINS(LCASE(?creator), LCASE("{artist}"))' for artist in artist_names])
        self.query += f'  FILTER NOT EXISTS {{ ?album schema:byArtist ?creator .\n'
        self.query += f'                     FILTER({artist_filters}) }}\n'

    def add_filter_not_contains_genre(self, genre_names):
        if not genre_names:
            raise ValueError("No genre names provided")

        genre_filters = " || ".join([f'CONTAINS(LCASE(?subject), LCASE("{genre}"))' for genre in genre_names])
        self.query += f'  FILTER NOT EXISTS {{ ?album schema:genre ?genreValue .\n'
        self.query += f'                   FILTER({genre_filters}) }}\n'

    def add_filter_genre(self, genres_names):
        if not genres_names:
            raise ValueError("No genre names provided")

        genre_filters = " || ".join([f'CONTAINS(LCASE(?subject), LCASE("{genre}"))' for genre in genres_names])
        self.query += f'  FILTER({genre_filters})\n'

    def add_filter_album(self, album_names):
        if not album_names:
            raise ValueError("No album names provided")

        album_filters = " || ".join([f'CONTAINS(LCASE(?vinylLabel), LCASE("{album}"))' for album in album_names])
        self.query += f'  FILTER({album_filters})\n'

    def add_filter_date2(self, operator, date_range):
        operators_mapping = {
            "after": ">",
            "before": "<",
            "to": "=",
            "from": "=",
            "equal": "=",
            "between": ">=",
        }
        filter = ""

        if operator in operators_mapping:
            if operator == "between" and len(date_range) == 2:
                filter += f" YEAR(?date) {operators_mapping[operator]} {date_range[0]} && YEAR(?date) {operators_mapping['before']} {date_range[1]}"
            else:
                filter += f" YEAR(?date) {operators_mapping[operator]} {date_range[0]}"
        else:
            raise ValueError("Invalid date filter operator")

        return filter

    def add_filters(self, preferences):
        if not preferences:
            raise ValueError("No filters provided")

        for preference in preferences:
            and_flag = False
            filter = ""

            if preference["preference"] == "love":
                if preference["artists"]:
                    filter += " || ".join(
                        [f'CONTAINS(LCASE(?creator), LCASE("{artist}"))' for artist in preference["artists"]])
                    and_flag = True
                if preference["genres"]:
                    if and_flag:
                        filter += " && "
                    filter += " || ".join(
                        [f'CONTAINS(?subject, "{genre}")' for genre in preference["genres"]])
                    and_flag = True

                if preference["years"]:
                    if and_flag:
                        filter += " && "
                    filter += self.add_filter_date2(preference["year_comparators"], preference["years"])

                self.query += f'  FILTER({filter})\n'
            elif preference["preference"] == "hate":
                filter = ""
                if preference["artists"]:
                    artist_filter = " || ".join(
                        [f'CONTAINS(?creator, "{artist}")' for artist in preference["artists"]])
                    if preference["years"]:
                        artist_filter += " && "
                        artist_filter += self.add_filter_date2(preference["year_comparators"], preference["years"])

                    filter += f' ?album dcterms:creator ?creator .\n'
                    filter += f'                     FILTER({artist_filter})\n'
                    and_flag = True
                if preference["genres"]:
                    genre_filter = " || ".join(
                        [f'CONTAINS(?subject, "{genre}")' for genre in preference["genres"]])
                    if preference["years"]:
                        genre_filter += " && "
                        genre_filter += self.add_filter_date2(preference["year_comparators"], preference["years"])

                    if and_flag:
                        filter += " && "
                    filter += f' ?album dcterms:subject ?genreValue .\n'
                    filter += f'                     FILTER({genre_filter})\n'

                self.query += f'  FILTER NOT EXISTS {{ {filter} }}\n'

    def add_limit(self, limit_value):
        if not isinstance(limit_value, int) or limit_value <= 0:
            raise ValueError("Invalid limit value. Limit must be a positive integer.")

        self.query += f"  LIMIT {limit_value}\n"

    def end_query(self):
        self.query = self.query + "}"

    def delete_query(self):
        self.query = ""
