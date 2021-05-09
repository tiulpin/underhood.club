<!-- markdownlint-disable -->

# API Overview

## Modules

- [`author`](./author.md#module-author): Everything related to Twitter API happens right here.
- [`page`](./page.md#module-page): Module with strange classes and methods to upload underhood.club data to Notion.
- [`tweet`](./tweet.md#module-tweet): UnderhoodTweet module.
- [`utils`](./utils.md#module-utils): It's not AI, it's Machine Learning.

## Classes

- [`author.Author`](./author.md#class-author): Class that represents an author inside some underhood account, tweets and has even few API calls when needed.
- [`page.Page`](./page.md#class-page): Underhood page as it is.
- [`tweet.UnderhoodTweet`](./tweet.md#class-underhoodtweet): Internal representation of a tweet which is used to publish it in Notion.
- [`utils.NotionTableOfContents`](./utils.md#class-notiontableofcontents): Notion table of contents block.

## Functions

- [`author.Author.__init__`](./author.md#function-__init__)
- [`author.extract_name`](./author.md#function-extract_name): Get author name from description or the first author tweet by using Spacy NER.
- [`author.extract_username`](./author.md#function-extract_username): Get username from description or the first author tweet by searching for @.
- [`page.Page.__init__`](./page.md#function-__init__)
- [`tweet.UnderhoodTweet.__init__`](./tweet.md#function-__init__)
- [`utils.clean_tweets`](./utils.md#function-clean_tweets): Prepare (clean) tweet texts for running topic modeling on it.
- [`utils.md_link`](./utils.md#function-md_link): Make Markdown link from the given URL.
- [`utils.print_topics`](./utils.md#function-print_topics): Pretty simple topic-modeling with LDA model on tweets: print the results right into stdout.
- [`utils.tweet_id_from_url`](./utils.md#function-tweet_id_from_url): Obtain tweet id from environment (from URL).
