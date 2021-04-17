#!/usr/bin/python
"""
notionhood – utility with strange classes and methods to upload underhood.club data to Notion
Waiting for an official Notion API library, then it will be refactored and become a library
"""
import sys
from os import environ
from pathlib import Path

from imgurpython import ImgurClient
from notion.client import NotionClient
from notionhood.notionhood import LocalConfig, Notionhood


def main():
    underhood = environ["TWEET"].split("/")[3]
    client = NotionClient(
        email=f"{underhood}@underhood.club",
        password=environ["NOTION_TOKEN"],
    )
    archive = client.get_block(f"https://www.notion.so/{environ[underhood]}")

    underhood = Notionhood(
        underhood=underhood,
        page=archive.collection.add_row(),
        local=LocalConfig(),
        links=[],
        imgur_client=ImgurClient(
            environ.get("IMGUR_API_ID"), environ.get("IMGUR_API_SECRET")
        ),
    )
    underhood.write_page(Path(sys.argv[1]).resolve())


if __name__ == "__main__":
    main()
