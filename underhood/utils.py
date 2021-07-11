"""It's not AI, it's Machine Learning."""
from collections import defaultdict
from pprint import pprint

from gensim.corpora import Dictionary
from gensim.models import LdaModel
from nltk.corpus import stopwords
from notion.block import BasicBlock

from underhood import LOCALE


stop_words = stopwords.words("russian")
stop_words.extend(LOCALE.stopwords)


class NotionTableOfContents(BasicBlock):
    """Notion table of contents block."""

    _type = "table_of_contents"


def md_link(display: str, real_url: str) -> str:
    """Make Markdown link from the given URL."""
    return f"[{display}]({real_url})"


def clean_tweets(tweets: list[str]) -> tuple[Dictionary, list[list[tuple[int, int]]]]:
    """Prepare (clean) tweet texts for running topic modeling on it.

    Args:
        tweets: list of strings (tweets texts)

    Returns:
        cleaned tweets
    """

    def is_ok(tweet: str) -> bool:
        """Check if tweet is not a reply or a retweet."""
        return not tweet.startswith(("@", "RT @"))

    def is_valid(word: str) -> bool:
        """Check if the given word contains only letters and not a stop word."""
        word = word.lower()
        return word.isalpha() and word not in stop_words

    def count_frequency(data) -> defaultdict:
        """Make frequency dict from the given words."""
        freq_dict: defaultdict[str, int] = defaultdict(int)
        for t in data:
            for tok in t:
                freq_dict[tok] += 1
        return freq_dict

    texts = [[w.lower() for w in t.split() if is_valid(w)] for t in tweets if is_ok(t)]
    freq = count_frequency(texts)
    processed_corpus = [[token for token in text if freq[token] > 1 and token] for text in texts]

    data_dictionary = Dictionary(processed_corpus)
    data_corpus = [data_dictionary.doc2bow(text) for text in processed_corpus]

    if data_dictionary[0]:  # an ugly way to initialize the collection
        print(data_dictionary[0])

    return data_dictionary, data_corpus


def print_topics(tweets: list[str]) -> None:
    """Pretty simple topic-modeling with LDA model on tweets: print the results right into stdout.

    Args:
        tweets: list of tweets
    """
    dictionary, corpus = clean_tweets(tweets)

    model = LdaModel(
        corpus=corpus,
        id2word=dictionary.id2token,
        alpha="auto",
        eta="auto",
        random_state=42,
        update_every=1,
        num_topics=LOCALE.topics,
    )
    pprint(model.print_topics())


def tweet_id_from_url(tweet_url: str) -> int:
    """Obtain tweet id from environment (from URL), e.g. .../1384130447999787017?s=20 -> 1384130447999787017."""
    return int(tweet_url.split("/")[-1].split("?")[0]) if tweet_url and isinstance(tweet_url, str) else 0


def slug_from_id(page_id: str) -> str:
    """Extract Notion page slug from the given id, e.g. lwuf-kj3r-fdw32-mnaks -> lwufkj3rfdw32mnaks."""
    return page_id.replace("-", "")
