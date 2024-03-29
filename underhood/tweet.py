"""UnderhoodTweet module."""
from dataclasses import dataclass, InitVar

from tweepy import Tweet

from underhood import IMAGE_FORMATS, LOCALE
from underhood.utils import md_link


@dataclass
class UnderhoodTweet:
    """Internal representation of a tweet which is used to publish it in Notion."""

    @dataclass
    class TweetURL:
        """Twitter URL dataclass."""

        shorten_url: str
        display_url: str
        source_url: str

    @dataclass
    class TweetPoll:
        """Twitter Poll dataclass."""

        o: InitVar[list[dict]]

        def __post_init__(self, o: list[dict]):
            total = sum(v.get("votes", 0) for v in o)
            self.results = [("{:.1%}".format(v.get("votes", 0) / total), v.get("label")) for v in o]

    tweet: InitVar[Tweet]
    quoted: InitVar[Tweet] = None

    def __post_init__(self, tweet: Tweet, quoted: Tweet = None):
        self.id = tweet.id
        self.conversation_id = tweet.conversation_id
        self.text = tweet.text
        self.date = tweet.created_at + LOCALE.td
        self.mentions = (
            [m.get("username") for m in tweet.entities.get("mentions", []) if m.get("username")]
            if tweet.entities
            else []
        )
        self.urls = (
            [
                UnderhoodTweet.TweetURL(u["url"], u["display_url"], u["expanded_url"])
                for u in tweet.entities.get("urls", [])
            ]
            if tweet.entities
            else []
        )
        self.media = [m for m in tweet.attachments.get("media", []) if m] if tweet.attachments else []
        self.polls = (
            [UnderhoodTweet.TweetPoll(p) for p in tweet.attachments.get("polls", []) if p] if tweet.attachments else []
        )
        self.quote = quoted.text if quoted else None
        self.quote_urls = (
            [
                UnderhoodTweet.TweetURL(u["url"], u["display_url"], u["expanded_url"])
                for u in quoted.entities.get("urls", [])
            ]
            if quoted and quoted.entities
            else []
        )
        self.links: list[str] = []
        for u in self.urls:
            self.text = self.text.replace(
                u.shorten_url, md_link(u.display_url, u.source_url) if "pic.twitter.com" not in u.display_url else ""
            )
            if u.source_url.endswith(IMAGE_FORMATS):
                self.media.append(u.source_url)
            elif not ("twitter.com" in u.source_url and "status" in u.source_url and u.source_url not in self.links):
                self.links.append(u.source_url)
        for n in self.mentions:
            self.text = self.text.replace(f"@{n}", md_link(f"@{n}", f"https://twitter.com/{n}"))
        for u in self.quote_urls:
            self.quote = self.quote.replace(u.shorten_url, md_link(u.display_url, u.source_url))
