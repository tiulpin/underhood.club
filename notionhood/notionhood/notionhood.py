from typing import Dict, FrozenSet, List, Optional, Set, Tuple, Type, Union

import string
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from time import sleep

import requests
import ru_core_news_sm
from imgurpython import ImgurClient
from notion.block import (
    BasicBlock,
    BookmarkBlock,
    CollectionViewBlock,
    DividerBlock,
    EmbedBlock,
    HeaderBlock,
    ImageBlock,
    QuoteBlock,
    SubheaderBlock,
    TextBlock,
)
from notion.collection import NotionDate
from tqdm import tqdm
from ujson import loads


@dataclass
class LocalConfig:  # 🇷🇺
    week_title: str = "Архив недели"
    links_title: str = "Ссылки"
    days: FrozenSet[str] = (
        "Понедельник",
        "Вторник",
        "Среда",
        "Четверг",
        "Пятница",
        "Суббота",
        "Воскресенье",
    )
    td = timedelta(hours=3)


def md_link(display: str, url: str) -> str:
    return f"[{display}]({url})"


def extract_names(
    description: str, tweet: dict
) -> Tuple[Optional[str], Optional[str]]:
    """
    Returns the first name in the given text (first tweet + description) using spacy named entity recognition and
    twitter username (from API field)

    :param description: string from profile description
    :param tweet: dumped tweet to extract data from
    :return: username and person name string if found
    """
    nlp = ru_core_news_sm.load()
    doc = nlp(f"{tweet.get('full_text', '')}")
    names = [X.text for X in doc.ents if X.label_ == "PER"]

    if names and len(names[0].split()) > 1:
        name = names[0]
    else:
        doc = nlp(description)
        names = [X.text for X in doc.ents if X.label_ == "PER"]
        name = names[-1] if names else None

    username = None
    if e := tweet.get("entities"):
        if u := e.get("user_mentions"):
            username = u[0].get("screen_name")
    elif "@" in description:
        username = [
            h
            for h in description.replace("(", " ").replace(")", " ").split()
            if h.startswith("@")
        ][0]

    return username, name


def get_date(twitter_date: str) -> datetime.date:
    """
    Creates datetime object from dumped tweet date string.
    :param twitter_date: date from tweet
    :return: datetime object
    """
    return datetime.strptime(twitter_date, "%a %b %d %H:%M:%S +0000 %Y")


def notion_handler(func):
    def inner_function(*args, **kwargs):
        while True:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(e)
                sleep(6)
                continue

    return inner_function


@dataclass
class Notionhood:
    page: CollectionViewBlock
    links: Set[str]
    local: LocalConfig
    underhood: str
    cloudflare_id: str
    cloudflare_token: str
    imgur_client: ImgurClient
    current_day: Optional[int] = None
    image_formats: Tuple[str] = (".png", ".jpg", ".jpeg")

    class TocBlock(BasicBlock):
        _type = "table_of_contents"

    @dataclass
    class Tweet:
        @dataclass
        class TweetMedia:
            type: str
            shorten_url: str
            source_url: str

        @dataclass
        class TweetURL:
            shorten_url: str
            display_url: str
            source_url: str

        id: str
        date: datetime
        text: str
        quote: str
        urls: List[TweetURL]
        quote_urls: List[TweetURL]
        media: List[TweetMedia]
        mentions: List[str]
        hashtags: List[str]
        images: List[str]

    def upload_img(self, image: str) -> str:
        response = self.imgur_client.upload_from_path(image, anon=True)

        return response["link"]

    @notion_handler
    def add(
        self, o: Type, content: Optional[str] = None
    ) -> Union[CollectionViewBlock, EmbedBlock, BookmarkBlock]:
        b = (
            self.page.children.add_new(o, title=content)
            if content
            else self.page.children.add_new(o)
        )
        return b

    def process_tweet(self, t: Dict) -> Optional[Tweet]:
        if not t["full_text"].startswith(("@", "RT @")):
            tweet = Notionhood.Tweet(
                id=t["id_str"],
                text=t["full_text"],
                quote=t["quoted_status"]["full_text"]
                if t["is_quote_status"] and "quoted_status" in t
                else None,
                date=get_date(t["created_at"]) + self.local.td,
                mentions=[
                    u["screen_name"] for u in t["entities"]["user_mentions"]
                ],
                hashtags=t["entities"]["hashtags"],
                urls=[
                    Notionhood.Tweet.TweetURL(
                        u["url"], u["display_url"], u["expanded_url"]
                    )
                    for u in t["entities"]["urls"]
                ],
                quote_urls=[
                    Notionhood.Tweet.TweetURL(
                        u["url"], u["display_url"], u["expanded_url"]
                    )
                    for u in t["quoted_status"]["entities"]["urls"]
                ]
                if t["is_quote_status"] and "quoted_status" in t
                else [],
                media=[
                    Notionhood.Tweet.TweetMedia(
                        m["type"], m["url"], m["media_url_https"]
                    )
                    for m in t["entities"]["media"]
                ]
                if "media" in t["entities"]
                else [],
                images=list(),  # could be from media, could be from URLs
            )
            for m in tweet.media:
                if m.type == "photo":
                    tweet.images.append(m.source_url)
                    tweet.text = tweet.text.replace(m.shorten_url, "")
            for u in tweet.urls:
                tweet.text = tweet.text.replace(
                    u.shorten_url, md_link(u.display_url, u.source_url)
                )
                if u.source_url.endswith(self.image_formats):
                    tweet.images.append(u.source_url)
                elif not (
                    "twitter.com" in u.source_url and "status" in u.source_url
                ):
                    self.links.add(u.source_url)
            for n in tweet.mentions:
                tweet.text = tweet.text.replace(
                    f"@{n}", md_link(f"@{n}", f"https://twitter.com/{n}")
                )
            for h in tweet.hashtags:
                tweet.text = tweet.text.replace(
                    f"#{h}",
                    md_link(f"#{h}", f"https://twitter.com/search?q=%23{h}"),
                )
            for u in tweet.quote_urls:
                tweet.quote = tweet.quote.replace(
                    u.shorten_url, md_link(u.display_url, u.source_url)
                )
            return tweet

    def write_page(self, author_dir: Path) -> None:
        def get_valid_avatar_path():
            avatar_path = str(
                author_dir / "images" / f"{author_dir.name}-image"
            )

            return avatar_path + (
                ".jpg" if Path(avatar_path + ".jpg").exists() else ".png"
            )

        @notion_handler
        def set_page_info(avatar_url: str):
            self.page.set("format.page_icon", avatar_url)
            self.page.title, self.page.nedelia = (
                name if name else "_",
                NotionDate(
                    start=get_date(tweets[0]["created_at"]).date(),
                    end=get_date(tweets[-1]["created_at"]).date(),
                ),
            )

        @notion_handler
        def check_day(weekday: int):
            if weekday != self.current_day:
                self.current_day = tweet.date.weekday()
                self.add(
                    SubheaderBlock, content=self.local.days[self.current_day]
                )
                self.add(DividerBlock)

        @notion_handler
        def add_tweet(tw: Notionhood.Tweet) -> None:
            self.add(
                TextBlock,
                content=md_link(
                    tweet.date.strftime("%H:%M"),
                    f"https://twitter.com/{self.underhood}/status/{tw.id}",
                ),
            ).set("format.block_color", "gray")
            if tw.quote:
                self.add(QuoteBlock, content=tw.quote)
            if len(tw.text):
                self.add(TextBlock, content=tw.text)
            for i in tw.images:
                self.add(ImageBlock).set_source_url(i)
            self.add(DividerBlock)

        @notion_handler
        def add_links() -> None:
            self.add(HeaderBlock, content=self.local.links_title)
            for k in self.links:
                self.add(BookmarkBlock).set_new_link(k)

        def update_urls(url: str, slug: str) -> None:
            cf_url = f"https://api.cloudflare.com/client/v4/accounts/{self.cloudflare_id}/workers/scripts/{self.underhood}"
            cf_headers = {
                "Authorization": f"Bearer {self.cloudflare_token}",
                "Content-Type": "application/javascript",
            }
            lines = requests.get(cf_url, headers=cf_headers).text.split("\n")
            lines[10] = f"{lines[10][:-2]}, '{url}': '{slug}'}};"
            requests.put(
                cf_url, headers=cf_headers, data="\n".join(lines).encode("utf8")
            )

        tweets = loads(
            (author_dir / f"{author_dir.name}-tweets.json").read_text()
        )["tweets"]
        description = loads(
            (author_dir / f"{author_dir.name}-info.json").read_text()
        )["description"]
        username, name = extract_names(description, tweets[0])
        set_page_info(self.upload_img(get_valid_avatar_path()))
        self.add(Notionhood.TocBlock).set("format.block_color", "gray")
        self.add(
            HeaderBlock,
            content=f"{self.local.week_title} {md_link(f'@{username}', f'https://twitter.com/{username}') if username else ''}",
        )
        for t in tqdm(tweets):
            if tweet := self.process_tweet(t):
                check_day(tweet.date.weekday())
                add_tweet(tweet)
        add_links()
        update_urls(
            username if username else self.page.id[:7],
            self.page.id.replace("-", ""),
        )
