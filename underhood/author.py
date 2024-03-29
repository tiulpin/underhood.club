"""Everything related to Twitter API happens right here."""
import string
from collections import defaultdict
from dataclasses import dataclass, InitVar
from functools import cached_property
import hashlib
from os import environ

from imgurpython import ImgurClient
from spacy import load
from tweepy import Client, Paginator, Tweet

from underhood import LOCALE
from underhood.tweet import UnderhoodTweet


EXPANSIONS = [
    "attachments.media_keys",
    "attachments.poll_ids",
    "entities.mentions.username",
]
TWEET_FIELDS = [
    "author_id",
    "created_at",
    "source",
    "entities",
    "referenced_tweets",
    "conversation_id",
]
MEDIA_FIELDS = ["media_key", "type", "url", "preview_image_url"]


@dataclass
class Author:
    """Class that represents an author inside some underhood account, tweets and has even few API calls when needed."""

    underhood: str
    twitter_token: InitVar[str]
    name: str = ""
    username: str = ""
    has_twitter: bool = True
    avatar: str = ""
    first_id: InitVar[int] = 0
    until_id: InitVar[int] = 0
    limit: int = 0

    def __post_init__(self, twitter_token: str, first_id: int = 0, until_id: int = 0):
        self.client = Client(twitter_token)
        self.user = self.client.get_user(
            username=self.underhood, expansions="pinned_tweet_id", user_fields=["profile_image_url", "description"]
        )
        first_id = first_id or self.user.data.pinned_tweet_id
        _first_tweet = self.get_tweet(first_id)

        all_tweets = [_first_tweet]
        for response in reversed(
            list(
                Paginator(
                    self.client.get_users_tweets,
                    id=self.user.data.id,
                    since_id=first_id,
                    until_id=until_id or None,
                    expansions=EXPANSIONS,
                    tweet_fields=TWEET_FIELDS,
                    media_fields=MEDIA_FIELDS,
                )
            )
        ):
            for t in response.data or []:
                if t.attachments:
                    if t.attachments.get("media_keys"):
                        t.attachments["media"] = [  # v2 api me no like it
                            m.get("url") or m.get("preview_image_url")
                            for m in response.includes.get("media", [])
                            for mkey in t.attachments.get("media_keys", [])
                            if m["media_key"] == mkey
                        ]
                    if t.attachments.get("poll_ids"):
                        t.attachments["polls"] = [
                            p.get("options")
                            for p in response.includes.get("polls", [])
                            if p.get("id") == t.attachments.get("poll_ids", [0])[0]  # TODO: refactor this
                        ]
                all_tweets.append(t)
        self.timeline = []
        self.conversations: defaultdict[int, list[UnderhoodTweet]] = defaultdict(list)
        for t in sorted(all_tweets, key=lambda k: k.id):
            if not t.text.startswith(("@", "RT @")):
                tweet = UnderhoodTweet(
                    tweet=t,
                    quoted=(  # Twitter V2 API :( or I don't know the best way to do this
                        self.get_tweet(t.referenced_tweets[0].id)
                        if t.referenced_tweets and t.referenced_tweets[0].type == "quoted"
                        else None
                    ),
                )
                self.timeline.append(tweet)
                self.conversations[tweet.conversation_id].append(tweet)
                if self.limit and len(self.timeline) >= self.limit:
                    break
        if not self.username:
            self.username = self.extract_username() or self.author_hash
        if not self.name:
            self.name = self.extract_name()
        if not self.avatar:
            self.imgur_client = ImgurClient(environ.get("IMGUR_API_ID"), environ.get("IMGUR_API_SECRET"))
            response = self.imgur_client.upload_from_url(
                self.user.data.profile_image_url.replace("_normal", ""), anon=True
            )
            self.avatar = response["link"]

    def get_tweet(self, tweet_id: int) -> Tweet:
        """Get tweet from Twitter API by id."""
        return self.client.get_tweet(
            id=tweet_id, expansions=EXPANSIONS, tweet_fields=TWEET_FIELDS, media_fields=MEDIA_FIELDS
        ).data

    @property
    def author_hash(self) -> str:
        """Internal first author tweet hash needed for different purposes."""
        self.has_twitter = False
        return hashlib.sha256(self.first_tweet.text.encode()).hexdigest()[:7]

    @property
    def description(self) -> str:
        """Profile description property."""
        return self.user.data.description

    @cached_property
    def first_tweet(self):
        """Last author tweet property."""
        return self.timeline[0]

    @cached_property
    def last_tweet(self):
        """Last author tweet property."""
        return self.timeline[-1]

    def extract_name(self):
        """Get author name from description or the first author tweet by using Spacy NER.

        Returns:
            name if found else an empty string
        """

        def search_name(d):
            """Extract first found two-word string (real person name) from Spacy entities analysis."""
            names = [x.text for x in d.ents if x.label_ == "PER" if len(x.text.split()) > 1]
            return names[0] if names else ""

        description, tweet = self.description, self.first_tweet
        nlp = load(LOCALE.spacy_model)
        for text in (description, tweet.text):
            doc = nlp(text)
            name = search_name(doc)
            if name:
                break
        return name

    def extract_username(self) -> str:
        """Get username from description or the first author tweet by searching for @.

        Returns:
            username if found else an empty string
        """
        description, tweet = self.description, self.first_tweet
        for text in (description, tweet.text):
            if "@" in text:
                text = text.translate(
                    str.maketrans(string.punctuation.replace("@", ""), " " * (len(string.punctuation) - 1))
                )
                return text.split("@")[1].split()[0]
        return ""
