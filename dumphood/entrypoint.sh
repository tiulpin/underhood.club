#!/bin/bash
cd /
IFS='/' read -r -a array <<< "$TWEET"
echo "Getting $AUTHOR tweets from ${array[3]}..."
cat > underhood.js << EOF1
const name = "${array[3]}"
const site = "!!!ANYUNDERHOOD.SITE"

const description = "!!!ANYUNDERHOOD.description"

module.exports = {
  "underhood": {
    name,
    description
  },
  "github": {
    user: "!!!ANYUNDERHOOD.github.user",
    repo: "!!!ANYUNDERHOOD.github.repo"
  },
  "curator": {
    email: "!!!ANYUNDERHOOD.curator.email",
    twitter: "!!!ANYUNDERHOOD.curator.twitter",
  },
  "site": {
    "title": "Сайт @" + name,
    "description": description,
    // TODO: RSS "feed_url": "https://" + site + "/rss.xml",
    "site_url": "https://" + site + "/",
  }
}
EOF1
echo "{username: '$AUTHOR', first: '${array[5]}'},"
cat > authors.js << EOF1
import authorId from './helpers/author-id';

export default authorId([
  { username: '$AUTHOR', first: '${array[5]}', post: true }
]);
EOF1
npm run update
