#!/usr/bin/python
"""
topichood – a small CLI utility, which does topic modelling on tweets dump, fastly prototyped for underhood.club
In case you know a better way to do topic modeling on tweets – contact me: viktor@tiulp.in
"""
from typing import List, Tuple

import sys
from collections import defaultdict
from pathlib import Path
from pprint import pprint

from gensim.corpora.dictionary import Dictionary
from gensim.models import LdaModel
from nltk.corpus import stopwords
from topichood import my_stopwords
from ujson import loads

TOPICS = 8


def clean_tweets(tweets) -> Tuple[Dictionary, List[List[Tuple[int, int]]]]:
    def is_ok(tweet: str) -> bool:
        return not tweet.startswith(("@", "RT @"))

    def is_valid(word: str) -> bool:
        word = word.lower()
        return word.isalpha() and word not in stop_words

    def count_frequency(data) -> defaultdict:
        freq_dict = defaultdict(int)
        for t in data:
            for tok in t:
                freq_dict[tok] += 1
        return freq_dict

    stop_words = stopwords.words("russian")
    stop_words.extend(my_stopwords)
    texts = [
        [w.lower() for w in t["full_text"].split() if is_valid(w)]
        for t in tweets
        if is_ok(t["full_text"])
    ]
    freq = count_frequency(texts)
    processed_corpus = [
        [token for token in text if freq[token] > 1 and token] for text in texts
    ]

    data_dictionary = Dictionary(processed_corpus)
    data_corpus = [data_dictionary.doc2bow(text) for text in processed_corpus]

    if data_dictionary[0]:  # an ugly way to initialize the collection
        pass

    return data_dictionary, data_corpus


def main() -> None:
    data_dir = Path(sys.argv[1]).resolve()
    print(
        loads((data_dir / f"{data_dir.name}-info.json").read_text())[
            "description"
        ]
    )

    dictionary, corpus = clean_tweets(
        loads((data_dir / f"{data_dir.name}-tweets.json").read_text())["tweets"]
    )

    model = LdaModel(
        corpus=corpus,
        id2word=dictionary.id2token,
        alpha="auto",
        eta="auto",
        random_state=42,
        update_every=1,
        num_topics=TOPICS,
    )
    pprint(model.print_topics())


if __name__ == "__main__":
    main()
