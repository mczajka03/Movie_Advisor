def get_movie_genres(input_tokens, sets):
    genres_found = []
    longest_genre = max(len(x.split()) for x in sets["genres"])

    for n in range(1, longest_genre + 1):
        for i in range(len(input_tokens) - n + 1):
            phrase = " ".join([input_tokens[j].text for j in range(i, i + n)])
            lemma_phrase = " ".join([input_tokens[j].lemma_ for j in range(i, i + n)])
            phrase2 = "-".join([input_tokens[j].text for j in range(i, i + n)])
            lemma_phrase2 = "-".join([input_tokens[j].lemma_ for j in range(i, i + n)])
            phrase3 = "".join([input_tokens[j].text for j in range(i, i + n)])
            lemma_phrase3 = "".join([input_tokens[j].lemma_ for j in range(i, i + n)])

            if phrase.lower() in sets["genres"] and phrase not in genres_found:
                genres_found.append(phrase)

            if lemma_phrase.lower() in sets["genres"] and lemma_phrase not in genres_found:
                genres_found.append(lemma_phrase)

            if phrase2.lower() in sets["genres"] and phrase2 not in genres_found:
                genres_found.append(phrase2)

            if lemma_phrase2.lower() in sets["genres"] and lemma_phrase2 not in genres_found:
                genres_found.append(lemma_phrase2)

            if phrase3.lower() in sets["genres"] and phrase3 not in genres_found:
                genres_found.append(phrase3)

            if lemma_phrase3.lower() in sets["genres"] and lemma_phrase3 not in genres_found:
                genres_found.append(lemma_phrase3)

            if phrase.lower() == "science fiction" or lemma_phrase.lower() == "science fiction" or phrase2.lower() == "science fiction" or lemma_phrase2.lower() == "science fiction" or phrase3.lower() == "science fiction" or lemma_phrase3.lower() == "science fiction":
                if "sci-fi" not in genres_found:
                    genres_found.append("sci-fi")

    return genres_found

