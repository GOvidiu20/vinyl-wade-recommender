class SPARQLQueryBuilder:
    def __init__(self, query):
        self.query = query

    def create_query(self):
        self.query = (
            "PREFIX dc: <http://purl.org/dc/elements/1.1/>\n"
            "PREFIX foaf: <http://xmlns.com/foaf/0.1/>\n"
            "PREFIX ns1: <http://purl.org/ontology/mo/>\n"
            "PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>\n"
            "SELECT ?vinylLabel ?creator ?date ?subject \n"
            "WHERE {\n"
            "   ?vinyl a ns1:Track ;\n"
            "         dc:title ?vinylLabel ;\n"
            "         foaf:name ?creator ;\n"
            "         ns1:genre ?subject ;\n"
            "         dc:date ?date ;\n"
        )

    def add_filter_artist(self, artists_names):
        if not artists_names:
            raise ValueError("No artist names provided")

        artist_filters = " || ".join([f'CONTAINS(LCASE(?creator), LCASE("{artist}"))' for artist in artists_names])
        self.query += f'  FILTER({artist_filters})\n'

    def add_filter_genre(self, genres_names):
        if not genres_names:
            raise ValueError("No genre names provided")

        genre_filters = " || ".join([f'CONTAINS(LCASE(?subject), LCASE("{genre}"))' for genre in genres_names])
        self.query += f'  FILTER({genre_filters})\n'

    def add_filter_date(self, operator, date_range):
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
                filter += f" xsd:integer(?date ) {operators_mapping[operator]} {date_range[0]} && xsd:integer(?date ) {operators_mapping['before']} {date_range[1]}"
            else:
                filter += f" xsd:integer(?date ) {operators_mapping[operator]} {date_range[0]}"
        else:
            raise ValueError("Invalid date filter operator")

        return filter

    def add_filters(self, preferences):
        if not preferences:
            raise ValueError("No filters provided")

        or_flag = False
        love_filter = ""
        hate_filter = ""
        for preference in preferences:
            and_flag = False

            if preference["preference"] == "love" or preference["preference"] == "like":

                if or_flag:
                    love_filter += " || "

                love_filter += '('

                if preference["artists"]:
                    love_filter += " || ".join(
                        [f'CONTAINS(LCASE(?creator ), LCASE("{artist}"))' for artist in preference["artists"]])
                    and_flag = True
                if preference["genres"]:
                    if and_flag:
                        love_filter += " && "
                    love_filter += " || ".join(
                        [f'CONTAINS(?subject , "{genre}")' for genre in preference["genres"]])
                    and_flag = True

                if preference["years"]:
                    if and_flag:
                        love_filter += " && "
                    love_filter += self.add_filter_date(preference["year_comparators"], preference["years"])

                love_filter += ')'
                or_flag = True
            elif preference["preference"] == "hate" or preference["preference"] == "dislike":
                filter = ""
                if preference["artists"]:
                    artist_filter = " || ".join(
                        [f'CONTAINS(?creator, "{artist}")' for artist in preference["artists"]])
                    if preference["years"]:
                        artist_filter += " && "
                        artist_filter += self.add_filter_date(preference["year_comparators"], preference["years"])

                    filter += f'    ?vinyl foaf:name ?creator .\n'
                    filter += f'    FILTER({artist_filter})\n'

                elif preference["genres"]:
                    genre_filter = " || ".join(
                        [f'CONTAINS(?subject, "{genre}")' for genre in preference["genres"]])
                    if preference["years"]:
                        genre_filter += " && "
                        genre_filter += self.add_filter_date(preference["year_comparators"], preference["years"])

                    filter += f'    ?vinyl ns1:genre ?subject .\n'
                    filter += f'    FILTER({genre_filter})\n'
                elif preference["years"]:
                    if and_flag:
                        filter += " && "
                    filter += f'    ?album schema:datePublished ?date .\n'
                    filter += f'    FILTER({self.add_filter_date(preference["year_comparators"], preference["years"])})\n'

                hate_filter += '  FILTER NOT EXISTS {' + filter + ' }\n'

        if love_filter != "":
            self.query += f'  FILTER({love_filter})\n'
        if hate_filter != "":
            self.query += hate_filter

    def add_limit(self, limit_value):
        if not isinstance(limit_value, int) or limit_value <= 0:
            raise ValueError("Invalid limit value. Limit must be a positive integer.")

        self.query += f"  LIMIT {limit_value}\n"

    def end_query(self):
        self.query = self.query + "}"

    def delete_query(self):
        self.query = ""
