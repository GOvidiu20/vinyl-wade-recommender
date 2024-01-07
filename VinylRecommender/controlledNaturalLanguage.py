import spacy
import flask
from flask import request, jsonify
from flask_cors import CORS

app = flask.Flask(__name__)
CORS(app)

nlp = spacy.load("en_core_web_sm")


def split_into_sentences(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)

    split_sentences = []

    current_sentence = ""
    for token in doc:
        # Check for delimiters
        if token.text.lower() in [',', 'and', 'or', '.']:
            if current_sentence:
                split_sentences.append(current_sentence.strip())
                current_sentence = ""
        else:
            current_sentence += token.text + " "
    if current_sentence:
        split_sentences.append(current_sentence.strip())

    return split_sentences


preferences = ["love", "like", "hate", "dislike"]
genres = ["rock", "pop", "jazz", "classical", "metal", "hiphop", "rap", "electronic", "dance", "folk", "country"]
comparators = ["from", "to", "before", "after"]
artists = ["Angela Gheorghiu", "Verdi", "Rossini", "Flood"]


def process_music_preference(user_input):
    current_entities = {"preference": None, "genres": set(), "artists": set(), "years": [], "year_comparators": None}
    processed_results = []
    split_sentences = split_into_sentences(user_input)

    for sentence in split_sentences:

        nlp = spacy.load("en_core_web_sm")
        doc = nlp(sentence)
        avoid_token_flag = 0
        for i, token in enumerate(doc):
            # Skip tokens that have already been processed
            if avoid_token_flag > 0:
                avoid_token_flag -= 1
                continue

            # Identify preferences
            if token.text.lower() in preferences:
                current_entities = {"preference": token.text.lower(), "genres": set(), "artists": set(), "years": [], "year_comparators": None}

            # Identify genres
            if token.text.lower() in genres:
                current_entities["genres"].add(token.text.lower())

            # Identify artists
            if token.ent_type_ == 'PERSON' or token.pos_ == 'PROPN':
                name = token.text
                while i + avoid_token_flag < len(doc) - 1:
                    next_token = token.nbor()
                    if next_token.ent_type_ == 'PERSON' or next_token.pos_ == 'PROPN':
                        name += " " + next_token.text
                        token = next_token
                        avoid_token_flag += 1
                    else:
                        break
                if name in artists:
                    current_entities["artists"].add(name)

            # Identify years and date ranges
            if token.text.lower() == 'from':
                if i < len(doc) - 1:
                    next_token = token.nbor()
                    if next_token.pos_ == 'NUM':
                        current_entities["years"].append(next_token.text)
                        avoid_token_flag += 1
                        current_entities["year_comparators"] = "equal"
                        if i + avoid_token_flag < len(doc) - 1:
                            next_token = next_token.nbor()
                            if next_token.text.lower() == 'to':
                                avoid_token_flag += 1
                                next_token = next_token.nbor()
                                if next_token.pos_ == 'NUM':
                                    current_entities["years"].append(next_token.text)
                                    avoid_token_flag += 1
                                    current_entities["year_comparators"] = "between"

            if token.text.lower() == 'before':
                if i < len(doc) - 1:
                    next_token = token.nbor()
                    if next_token.pos_ == 'NUM':
                        current_entities["years"].append(next_token.text)
                        current_entities["year_comparators"] = "before"

            if token.text.lower() == 'after':
                if i < len(doc) - 1:
                    next_token = token.nbor()
                    if next_token.pos_ == 'NUM':
                        current_entities["years"].append(next_token.text)
                        current_entities["year_comparators"] = "after"

        processed_results.append(current_entities)

        # query = ""
        # if current_entities["genres"]:
        #     query += "genre in ("
        #     for genre in current_entities["genres"]:
        #         query += genre + ","
        #
        #     query = query[:-1]
        #     query += ") "
        # if current_entities["artists"]:
        #     query += "and artist in ("
        #     for artist in current_entities["artists"]:
        #         query += artist + ","
        #     query = query[:-1]
        #     query += ") "
        # if current_entities["years"]:
        #     if current_entities["year_comparators"] == "equal":
        #         query += f"and year={current_entities['years'][0]} "
        #     elif current_entities["year_comparators"] == "between":
        #         query += f"and year >= {current_entities['years'][0]} and year <= {current_entities['years'][1]} "
        #     elif current_entities["year_comparators"] == "before":
        #         query += f"and year < {current_entities['years'][0]} "
        #     elif current_entities["year_comparators"] == "after":
        #         query += f"and year > {current_entities['years'][0]} "
        # print(f"Query: {query}\n")

        current_entities = {"preference": current_entities["preference"], "genres": current_entities["genres"], "artists": set(), "years": [],
                            "year_comparators": None}

    return processed_results


# # Example
# user_input = ("I love classical music, especially opera by Rossini or Verdi and performed by Angela Gheorghiu from "
#               "1999 and hate music from Verdi from 2000 to 2005. "
#               "I sometimes like rock and post-rock. I like only metal albums released before 2000. I "
#               "always hate rap and pop."
#               "I dislike songs produced by Flood after 2000")
# process_music_preference(user_input)

def get_recommendations(text):
    processed_results = process_music_preference(text)
    print(processed_results)
    # query

    recommendation = [
        {
            "title": "title 1",
            "artist": "artist 1",
            "genre": "genre 1",
            "year": "year 1",
        }
    ]

    return recommendation

@app.route('/text-processing', methods=['POST'])
def process_text():
    user_input = request.json['text']
    recommendations = get_recommendations(user_input)
    return recommendations


if __name__ == '__main__':
    app.run()
