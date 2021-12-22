"""Underhood entrypoint."""
from datetime import datetime
from json import dumps, loads
from os import getenv
from pathlib import Path

from notion.client import NotionClient
import pretty_errors
import sentry_sdk

# noinspection PyPackageRequirements
from telegram import Bot, ParseMode

# noinspection PyPackageRequirements
from telegram.error import TelegramError
from typer import Argument, Option, Typer

from underhood import LOCALE
from underhood.author import Author
from underhood.page import Page
from underhood.utils import tweet_id_from_url


pretty_errors.configure(filename_display=pretty_errors.FILENAME_EXTENDED, line_number_first=True, display_link=True)

sentry_dsn: str = getenv("SENTRY_DSN", "")
if sentry_dsn:
    sentry_sdk.init(sentry_dsn, traces_sample_rate=1.0)  # since we don't need speed, let's send everything!

app = Typer()


@app.command()
def dump(
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
    no_email_auth: bool = Option(False, "-ne", envvar="NO_EMAIL"),
    limit: int = Option(0, "--limit", "-l", envvar="LIMIT", help="Limit number of tweets to dump"),
):
    urls_path = Path(".") / underhood / "urls.json"
    telethreads_path = Path(".") / underhood / "telethreads.json"
    underhood_page = Page(
        author=Author(
            underhood,
            name=name,
            username=username,
            avatar=avatar,
            twitter_token=twitter_token,
            first_id=tweet_id_from_url(first_tweet),
            until_id=tweet_id_from_url(until_tweet),
            limit=limit,
        ),
        client=(
            NotionClient(token_v2=notion_token)
            if no_email_auth
            else NotionClient(email=f"{underhood}@underhood.club", password=notion_token)
        ),
        urls=loads(urls_path.read_text()),
    )
    underhood_page.write()
    # TODO: okay, we definitely need some S3 here
    # also, move it to a separated module
    urls_path.write_text(dumps(underhood_page.urls, indent=4))
    if telethreads_path.exists():
        telethreads = loads(telethreads_path.read_text())
        telethreads["current_first_tweet"] = underhood_page.author.first_tweet.text
        if datetime.today().weekday() == 1:
            telethreads["threads"] = []
        for t in underhood_page.threads:
            if all(m["message"] != t["message"] for m in telethreads["threads"]):
                telethreads["threads"].append(
                    {
                        "iv_url": f"https://t.me/iv?url={telethreads['base']}{t['url']}&{telethreads['rhash']}",
                        "url": f"{telethreads['base']}{t['url']}",
                        "message": t["message"],
                        "sent": False,
                    }
                )
        if datetime.today().weekday() == 0:
            telethreads["threads"].append(
                {
                    "iv_url": f"https://t.me/iv?url={telethreads['base']}/{underhood_page.author.username}&"
                    f"{telethreads['rhash']}",
                    "url": f"{telethreads['base']}/{underhood_page.author.username}",
                    "message": LOCALE.week_uploaded,
                    "sent": False,
                }
            )
        telethreads_path.write_text(dumps(telethreads, indent=4, ensure_ascii=False))


@app.command()
def telethread(
    underhood: str = Argument(..., envvar="UNDERHOOD", help="underhood name"),
    telegram_token: str = Option(..., "--telegram-token", "-tt", envvar="TELEGRAM_TOKEN", help="Telegram token"),
):
    """Send telethreads – runs daily."""
    telethreads_path = Path(".") / underhood / "telethreads.json"
    telethreads = loads(telethreads_path.read_text())
    bot = Bot(token=telegram_token)
    problems = []
    if datetime.today().weekday() == 1:
        message = bot.sendMessage(
            chat_id=telethreads["channel"], text=telethreads["current_first_tweet"], parse_mode=ParseMode.MARKDOWN
        )
        bot.pinChatMessage(chat_id=telethreads["channel"], message_id=message.message_id)
    if telethreads["threads"] and any(not t["sent"] for t in telethreads["threads"]):
        bot.sendMessage(
            chat_id=telethreads["channel"],
            text=telethreads["greetings"],
            parse_mode=ParseMode.MARKDOWN,
        )
        for t in telethreads["threads"]:
            if not t["sent"]:
                try:
                    bot.sendMessage(
                        chat_id=telethreads["channel"],
                        text=f"[▸]({t['iv_url']}) {(t['message'])}",
                        parse_mode=ParseMode.MARKDOWN,
                    )
                except TelegramError as e:
                    problems.append(e)
                    pass
                t["sent"] = True
    telethreads_path.write_text(dumps(telethreads, indent=4, ensure_ascii=False))
    if problems:
        print(problems)
        raise problems[0]


if __name__ == "__main__":
    app()
