import spacy
import csv
from google.cloud import storage

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
comparators = ["from", "to", "before", "after"]

storage_client = storage.Client()
bucket = storage_client.get_bucket("vinyl-recommender")

artists = bucket.blob("artists.txt").download_as_string().decode("utf-8").split("\r\n")
genres = bucket.blob("genres.txt").download_as_string().decode("utf-8").split("\r\n")

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
                current_entities = {"preference": token.text.lower(), "genres": set(), "artists": set(), "years": [],
                                    "year_comparators": None}

            # Identify genres
            if token.text.lower() in genres:
                current_entities["genres"].add(token.text.lower())

            # Identify artists
            if token.text[0].isupper():
                name = token.text
                while i + avoid_token_flag < len(doc) - 1:
                    next_token = token.nbor()
                    if next_token.text[0].isupper() or next_token.text == '&':
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
        current_entities = {"preference": current_entities["preference"], "genres": current_entities["genres"],
                            "artists": set(), "years": [],
                            "year_comparators": None}

    return processed_results

# def add_data_to_files():
#     csv_file_path = 'C:\\Users\\Ovidiu\Desktop\\vinyl-wade-recommender\\VinylRecommender\\data\\query.csv'
#     artists_path = 'C:\\Users\\Ovidiu\Desktop\\vinyl-wade-recommender\\VinylRecommender\\data\\artists.txt'
#     genres_path = 'C:\\Users\\Ovidiu\Desktop\\vinyl-wade-recommender\\VinylRecommender\\data\\genres.txt'
#
#     with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
#         csv_reader = csv.DictReader(csvfile)
#
#         for row in csv_reader:
#             if row['artistLabel'] not in artists2:
#                 artists2.append(row['artistLabel'])
#             if row['genreLabel'] not in genres2:
#                 genres2.append(row['genreLabel'])
#     print(len(artists2), len(genres2))
#     with open(artists_path, 'w', encoding='utf-8') as filehandle:
#         for artist in artists2:
#             filehandle.write(f'{artist}\n')
#     with open(genres_path, 'w', encoding='utf-8') as filehandle:
#         for genre in genres2:
#             filehandle.write(f'{genre}\n')