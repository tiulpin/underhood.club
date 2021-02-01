import { outputFile } from 'fs-extra';
import { isEmpty, concat, reverse, last } from 'ramda';
import moment from 'moment';
import dec from 'bignum-dec';
import { sync as rm } from 'rimraf';

import { underhood } from '../../underhood.js';
const underhoodName = underhood.name;

import tokens from 'twitter-tokens';
import getTweets from '../../helpers/get-tweets';
import getInfo from 'get-twitter-info';
import saveMedia from '../../helpers/save-media';
import getFollowers from '../../helpers/get-followers';

import ensureFilesForFirstUpdate from '../../helpers/ensure-author-files';
import getAuthorArea from '../../helpers/get-author-area';
import saveAuthorArea from '../../helpers/save-author-area';

/// Updates one author
const update = (author, maxId) => {
  const { authorId, first } = author;

  ensureFilesForFirstUpdate(authorId);

  const tweets = getAuthorArea(authorId, 'tweets').tweets || [];

  const tweetsSinceId = isEmpty(tweets) ? dec(first) : last(tweets).id_str;
  const tweetsMaxId = maxId && dec(maxId);
  getTweets(
    tokens,
    underhoodName,
    tweetsSinceId,
    tweetsMaxId,
    (err, newTweetsRaw) => {
      if (err) throw err;
      const concattedTweets = concat(tweets, reverse(newTweetsRaw));
      saveAuthorArea(authorId, 'tweets', { tweets: concattedTweets });
    }
  );

  getInfo(tokens, underhoodName, (err, info) => {
    if (err) throw err;
    saveAuthorArea(authorId, 'info', info);
  });

  rm(`./dump/images/${authorId}*`);
  saveMedia(tokens, underhoodName, authorId, (err, media) => {
    if (err) throw err;
    saveAuthorArea(authorId, 'media', media);
  });

  getFollowers(tokens, underhoodName, (err, followersIds) => {
    if (err) throw err;
    saveAuthorArea(authorId, 'followers', { followersIds });
  });

  outputFile('./dump/.timestamp', moment().unix(), (err) => {
    console.log(`${err ? '✗' : '✓'} timestamp`);
  });
};

export default update;
