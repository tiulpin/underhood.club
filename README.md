<div align="center">

# 🔥 [underhood.club](https://underhood.club/)

The monorepo contains everything what's needed.

### All stacks badges
[![DeepSource](https://deepsource.io/gh/tiulpin/underhood.club.svg/?label=active+issues&token=O2vpl_Y605V0lrWbaTTOTNTh)](https://deepsource.io/gh/tiulpin/underhood.club/?ref=repository-badge)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/tiulpin/overhood/blob/master/.pre-commit-config.yaml)
[![License](https://img.shields.io/github/license/tiulpin/underhood.club)](https://github.com/tiulpin/underhood.club/blob/main/LICENSE)
[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/tiulpin/overhood/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)

## Python badges

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)

## Node.js badges

No badges!

</div>

### Motivation

I wanted a way of storing tweets per weeks, like [@abroadunderhood](http://abroadunderhood.ru), but I
- don't want to host anything at all/spend resources for hostings
- need a good way of editing existing pages
- want it to look nice
- am not a frontend-developer, know nothing about JavaScript and so on
- can dockerize things and make them work

That's why I've created three main containers, that help make a website like 🔥[underhood.club](https://underhood.club/)
- [`dumphood`](https://github.com/tiulpin/underhood.club/main/dumphood) – downloading tweets using Twitter API
- [`topichood`](https://github.com/tiulpin/underhood.club/main/topichood) – topic modeling on tweets
- [`notionhood`](https://github.com/tiulpin/underhood.club/main/notionhood) – uploading already dumped tweets to Notion with a bit of NLP (NER for finding pages names)

### Articles

- 🇬🇧 This README 
- 🇷🇺 [The blogpost about the whole project](https://vas3k.club/project/4060/) (a bit outdated, will be updated soon)

## 🛡 License

[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Ftiulpin%2Funderhood.club.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2Ftiulpin%2Funderhood.club?ref=badge_large)

## 🙏 Thanks
- to all authors at [@mobileunderhood](https://twitter.com/mobileunderhood), [@produnderhood](https://twitter.com/produnderhood), [@itunderhood](https://twitter.com/iunderhood), [@dsunderhood](https://twitter.com/dsunderhood) for the great content, without it the website would not be that good
- [`notion-py`](http://github.com/jamalex/notion-py/) – the project could not exist without this particular library
- [`anyunderhood`](https://github.com/anyunderhood/anyunderhood) – the template is the base of `dumphood` image for tweets downloading
- [`python-package-template`](https://github.com/TezRomacH/python-package-template) – got some GitHub configs/dependencies from there
