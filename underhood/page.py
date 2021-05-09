"""Module with strange classes and methods to upload underhood.club data to Notion.
Waiting for an official Notion API library, then it will be refactored and become a nice library...
"""
from dataclasses import dataclass
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
from notion.client import NotionClient
from notion.collection import NotionDate
from tenacity import retry, wait_random
from tqdm import tqdm

from underhood import LOCALE
from underhood.author import Author
from underhood.tweet import UnderhoodTweet
from underhood.utils import md_link, NotionTableOfContents, print_topics


@dataclass
class Page:
    """Underhood page as it is."""

    author: Author
    client: NotionClient
    urls: dict[str, str]
    current_day: int = -1

    def __post_init__(self):
        self.threads = []
        self.links = []
        self.archive = self.client.get_block(f"https://www.notion.so/{self.urls['/archive']}")
        self.npage = self.archive.collection.add_row()

    @retry(wait=wait_random(min=3, max=7))
    def add(
        self, o: Type, content: Optional[str] = None, page=None
    ) -> Union[CollectionViewBlock, EmbedBlock, BookmarkBlock]:
        if page is None:
            page = self.npage
        b = page.children.add_new(o, title=content) if content else page.children.add_new(o)
        return b

    def write(self) -> None:
        @retry(wait=wait_random(min=3, max=7))
        def set_page_info(page=None):
            if page is None:
                self.npage.set("format.page_icon", self.author.avatar)
                self.npage.title = self.author.name
                self.npage.nedelia = NotionDate(
                    start=self.author.first_tweet.date.date(),
                    end=self.author.last_tweet.date.date(),
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
            self.add(DividerBlock, page=thread_page)
            for tt in thread:
                self.add(
                    TextBlock,
                    content=md_link(
                        tt.date.strftime("%H:%M"),
                        f"https://twitter.com/{self.author.underhood}/status/{tt.id}",
                    ),
                    page=thread_page,
                ).set("format.block_color", "gray")
                if tt.quote:
                    self.add(QuoteBlock, content=tt.quote, page=thread_page)
                if tt.text:
                    self.add(TextBlock, content=tt.text, page=thread_page)
                for i in tt.media:
                    self.add(ImageBlock, page=thread_page).set_source_url(i)
                for p in tt.polls:
                    for r in p.results:  # improve it someday when polls output will be clear
                        self.add(TextBlock, content=f"🤔 `{r[0]}` {r[1]}", page=thread_page)
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
                        f"https://twitter.com/{self.author.underhood}/status/{tw.id}",
                    ),
                ).set("format.block_color", "gray")
                if tw.quote:
                    self.add(QuoteBlock, content=tw.quote)
                if tw.text:
                    self.add(TextBlock, content=tw.text)
                for i in tw.media:
                    self.add(ImageBlock).set_source_url(i)
                for p in tw.polls:
                    for r in p.results:  # improve it someday when polls output will be clear
                        self.add(TextBlock, content=f"🤔 `{r[0]}` {r[1]}")
                self.add(DividerBlock)

        @retry(wait=wait_random(min=3, max=7))
        def add_links() -> None:
            self.add(HeaderBlock, content=LOCALE.links_title)
            for k in self.links:
                self.add(BookmarkBlock).set_new_link(k)

        print(f"{self.author.description}")
        set_page_info()
        self.add(NotionTableOfContents).set("format.block_color", "gray")
        self.add(
            HeaderBlock,
            content=f"{LOCALE.week_title} "
            f"{md_link(f'@{self.author.username}', f'https://twitter.com/{self.author.username}') if self.author.username else ''}",
        )
        for t in tqdm(self.author.timeline):
            check_day(t.date.weekday())
            add_tweet(t)
            self.links.extend(t.links)
            if (
                t is self.author.conversations[t.conversation_id][-1]
                and len(self.author.conversations[t.conversation_id]) > LOCALE.thread_count
            ):
                add_thread(self.author.conversations[t.conversation_id])
                self.add(DividerBlock)
        add_links()
        if not self.author.username:
            self.author.username = self.npage.id.replace("-", "")[:7]
        for n, th in enumerate(self.threads):
            self.urls[f"/{self.author.username}-thread-{n + 1}"] = th.id.replace("-", "")
        self.urls[f"/{self.author.username}"] = self.npage.id.replace("-", "")

        print_topics([t.text for t in self.author.timeline])
