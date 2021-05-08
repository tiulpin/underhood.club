"""Module with strange classes and methods to upload underhood.club data to Notion.
Waiting for an official Notion API library, then it will be refactored and become a nice library...
"""
from dataclasses import dataclass, field
from typing import Optional, Type, Union

from notion.block import (
    BookmarkBlock,
    CollectionViewBlock,
    DividerBlock,
    EmbedBlock,
    HeaderBlock,
    ImageBlock,
    PageBlock,
    QuoteBlock,
    SubheaderBlock,
    TextBlock,
)
from notion.collection import NotionDate
from spacy import load
from tenacity import retry, wait_random
from tqdm import tqdm

from underhood import LOCALE
from underhood.author import Author
from underhood.tweet import UnderhoodTweet
from underhood.utils import md_link, NotionTableOfContents, print_topics


@dataclass
class Page:
    """Underhood page as it is."""

    npage: CollectionViewBlock
    underhood: str
    threads: list[Union[CollectionViewBlock, EmbedBlock, BookmarkBlock]] = field(default_factory=list)
    links: list[str] = field(default_factory=list)
    current_day: int = -1

    @retry(wait=wait_random(min=3, max=7))
    def add(
        self, o: Type, content: Optional[str] = None, page=None
    ) -> Union[CollectionViewBlock, EmbedBlock, BookmarkBlock]:
        if page is None:
            page = self.npage
        b = page.children.add_new(o, title=content) if content else page.children.add_new(o)
        return b

    def write(self, author: Author) -> str:
        @retry(wait=wait_random(min=3, max=7))
        def set_page_info(page=None):
            if page is None:
                self.npage.set("format.page_icon", author.avatar)
                self.npage.title = name if name else "_"
                self.npage.nedelia = NotionDate(
                    start=author.first_tweet.date.date(),
                    end=author.last_tweet.date.date(),
                )
            else:
                page.set("format.page_icon", "🔥")
                page.title = f"{LOCALE.thread} #{len(self.threads) + 1}"

        @retry(wait=wait_random(min=3, max=7))
        def check_day(weekday: int) -> None:
            if weekday != self.current_day:
                self.current_day = weekday
                self.add(SubheaderBlock, content=LOCALE.days[self.current_day])
                self.add(DividerBlock)

        def add_thread(thread: list[UnderhoodTweet]):
            thread_page = self.add(PageBlock)
            thread_page.set("format.block_color", "gray")
            set_page_info(thread_page)
            for tt in thread:
                self.add(
                    TextBlock,
                    content=md_link(
                        tt.date.strftime("%H:%M"),
                        f"https://twitter.com/{self.underhood}/status/{tt.id}",
                    ),
                    page=thread_page,
                ).set("format.block_color", "gray")
                if tt.quote:
                    self.add(QuoteBlock, content=tt.quote, page=thread_page)
                if tt.text:
                    self.add(TextBlock, content=tt.text, page=thread_page)
                for i in tt.media:
                    self.add(ImageBlock, page=thread_page).set_source_url(i)
                self.add(DividerBlock, page=thread_page)
            thread_page.children.add_alias(self.npage)
            self.threads.append(thread_page)

        @retry(wait=wait_random(min=3, max=7))
        def add_tweet(tw: UnderhoodTweet) -> None:
            if tw:
                self.add(
                    TextBlock,
                    content=md_link(
                        tw.date.strftime("%H:%M"),
                        f"https://twitter.com/{self.underhood}/status/{tw.id}",
                    ),
                ).set("format.block_color", "gray")
                if tw.quote:
                    self.add(QuoteBlock, content=tw.quote)
                if tw.text:
                    self.add(TextBlock, content=tw.text)
                for i in tw.media:
                    self.add(ImageBlock).set_source_url(i)
                self.add(DividerBlock)

        @retry(wait=wait_random(min=3, max=7))
        def add_links() -> None:
            self.add(HeaderBlock, content=LOCALE.links_title)
            for k in self.links:
                self.add(BookmarkBlock).set_new_link(k)

        print(f"{author.description}")
        username, name = extract_names(author)
        set_page_info()
        self.add(NotionTableOfContents).set("format.block_color", "gray")
        self.add(
            HeaderBlock,
            content=f"{LOCALE.week_title} "
            f"{md_link(f'@{username}', f'https://twitter.com/{username}') if username else ''}",
        )
        for c in tqdm(author.timeline.keys()):
            for t in author.timeline[c]:
                check_day(t.date.weekday())
                add_tweet(t)
                self.links.extend(t.links)
                if t is author.timeline[c][-1] and len(author.timeline[c]) > LOCALE.thread_count:
                    add_thread(author.timeline[c])
                    self.add(DividerBlock)
        add_links()
        print_topics([t.text for c in author.timeline.keys() for t in author.timeline[c]])

        return username if username else self.npage.id[:7]


def extract_names(author: Author) -> tuple[Optional[str], Optional[str]]:
    """Returns the first name in the given text (first tweet + description) using spacy named entity recognition and
    twitter username (from API field).

    Args:
        author: Underhood author object

    Returns:
        name and username, if found
    """
    description, tweet = author.description, author.first_tweet
    username = None
    if e := tweet.mentions:
        username = e[0].get("username")
    elif "@" in description:
        username = [h[1:] for h in description.replace("(", " ").replace(")", " ").split() if h.startswith("@")][0]

    nlp = load(LOCALE.spacy_model)
    doc = nlp(tweet.text)
    names = [X.text for X in doc.ents if X.label_ == "PER"]

    if names and len(names[0].split()) > 1:
        name = names[0]
    else:
        doc = nlp(description)
        names = [X.text for X in doc.ents if X.label_ == "PER"]
        name = names[-1] if names else None

    return username, name
