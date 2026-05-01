<div align="center">

# 🔥 underhood.club — Archived

> **This project has been archived and is no longer maintained.**
>
> The content has moved to **[underhood.notion.site/main](https://underhood.notion.site/main)** — please go there instead.

</div>

---

## What was this?

**underhood.club** was a platform that aggregated weekly rotating Twitter accounts in the Russian-speaking tech community — accounts like [@mobileunderhood](https://twitter.com/mobileunderhood), [@produnderhood](https://twitter.com/produnderhood), [@itunderhood](https://twitter.com/iunderhood), and [@dsunderhood](https://twitter.com/dsunderhood) — and published their tweets as a searchable, nicely formatted website.

The project has no plans to evolve further and has been sunset in favor of Notion-hosted content at [underhood.notion.site/main](https://underhood.notion.site/main).

## How it worked

The stack was a Python monorepo with three main parts:

- **`underhood/`** — a Python package that used [`notion-py`](https://github.com/jamalex/notion-py/) to fetch tweets via the Twitter API, perform NLP (Named Entity Recognition to extract page titles), and sync content into Notion databases.
- **`fronthood/`** — a [Next.js](https://nextjs.org/) frontend based on [`nextjs-notion-starter-kit`](https://github.com/transitive-bullshit/nextjs-notion-starter-kit), deployed on [Vercel](https://vercel.com/), that rendered Notion pages as a fast, user-friendly website for each `*.underhood.club` subdomain.
- **GitHub Actions workflows** — scheduled jobs that ran the Python sync container periodically to keep each account's content up to date.

The whole thing ran in a single Docker container with no persistent hosting required beyond Vercel for the frontend.

## License

[MIT](https://github.com/tiulpin/underhood.club/blob/main/LICENSE)
