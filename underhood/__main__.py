"""Underhood entrypoint."""
from json import dumps, loads
from pathlib import Path

from notion.client import NotionClient
import pretty_errors
import sentry_sdk
from typer import Argument, Option, run

from underhood.author import Author
from underhood.page import Page
from underhood.utils import tweet_id_from_url


pretty_errors.configure(filename_display=pretty_errors.FILENAME_EXTENDED, line_number_first=True, display_link=True)


def main(
    underhood: str = Argument(..., envvar="UNDERHOOD", help="underhood name"),
    notion_token: str = Option(..., "--notion-token", "-nt", envvar="NOTION_TOKEN", help="unofficial Notion API token"),
    twitter_token: str = Option(..., "--twitter-token", "-tt", envvar="TWITTER_TOKEN", help="Twitter APIv2 token"),
    username: str = Option("", "--username", "-u", envvar="USERNAME", help="If none, then will be extracted later"),
    name: str = Option("", "--name", "-n", envvar="NAME", help="If none, then will be extracted later"),
    avatar: str = Option("", "--avatar", "-a", envvar="AVATAR", help="If none, then will be extracted later"),
    first_tweet: str = Option(
        None, "--first-tweet", "-ft", envvar="FIRST_TWEET", help="Tweet to start dumping from (default: from pinned)"
    ),
    until_tweet: str = Option(
        None, "--until-tweet", "-ut", envvar="LAST_TWEET", help="Tweet to dump to [not included to dump]"
    ),
    sentry_dsn: str = Option(None, "--sentry-dsn", "-s", envvar="SENTRY_DSN"),
    no_email_auth: bool = Option(False, "-ne", envvar="NO_EMAIL"),
):
    if sentry_dsn:
        sentry_sdk.init(sentry_dsn, traces_sample_rate=1.0)  # since we don't need speed, let's send everything!
    urls_path = Path(".") / underhood / "urls.json"
    underhood_page = Page(
        author=Author(
            underhood,
            name=name,
            username=username,
            avatar=avatar,
            twitter_token=twitter_token,
            first_id=tweet_id_from_url(first_tweet),
            until_id=tweet_id_from_url(until_tweet),
        ),
        client=(
            NotionClient(token_v2=notion_token)
            if no_email_auth
            else NotionClient(email=f"{underhood}@underhood.club", password=notion_token)
        ),
        urls=loads(urls_path.read_text()),
    )
    underhood_page.write()
    urls_path.write_text(dumps(underhood_page.urls, indent=4))


def launch():
    run(main)


if __name__ == "__main__":
    launch()
