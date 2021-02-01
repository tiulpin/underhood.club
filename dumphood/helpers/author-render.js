import moment from 'moment';
import {
  pipe, filter, groupBy, prop, converge, inc, dec, length,
  findIndex, propEq, path, map, head, split, nth, replace, toUpper, tail,
  concat
} from 'ramda';
import numd from 'numd';
import renderTweet from 'tweet.md';
import getLinks from './get-links';
import { html } from 'commonmark-helpers';
import ungroupInto from './ungroup-into';
import unidecode from 'unidecode';
import trimTag from 'trim-html-tag';
import { parse } from 'url';
import { underhood } from '../underhood';
import authors from './input-authors';

const getQuotedUser = pipe(
  path(['entities', 'urls']),
  map(prop('expanded_url')),
  map(replace('/mobile.twitter.com/', '/twitter.com/')),
  filter((url) => parse(url).host === 'twitter.com'),
  head,
  pipe(parse, prop('path'), split('/'), nth(1))
);

moment.locale('ru');

const weekday = date => moment.utc(new Date(date)).format('dddd');
const tweetLink = (tweet) => `https://twitter.com/${underhood.name}/status/${tweet.id_str}`;
const tweetTime = (tweet) => moment.utc(new Date(tweet.created_at)).format('H:mm');

const authorsToPost = filter((author) => author.post !== false, authors);

const authorIndex = author => findIndex(propEq('authorId', author.authorId))(authorsToPost);
const isFirstAuthor = author => authorIndex(author) === dec(length(authorsToPost));
const isLastAuthor = author => author.authorId === prop('authorId', head(authorsToPost));
const nextAuthor = author => {
  if (!isLastAuthor(author)) return nth(dec(authorIndex(author)), authorsToPost);
};
const prevAuthor = (author) => {
  if (!isFirstAuthor(author))
    return nth(inc(authorIndex(author)), authorsToPost);
};

const d = input => moment.utc(new Date(input)).format('D MMMM YYYY')
const gd = input => moment.utc(new Date(input)).format('YYYY-MM-DD');
const tweetsUnit = numd('твит', 'твита', 'твитов');
const capitalize = converge(concat, [pipe(head, toUpper), tail]);

const filterTimeline = item => (item.text[0] !== '@') || (item.text.indexOf(`@${underhood.name}`) === 0);
const fullText = item => {
  item.text = item.full_text || item.text;

  if (item.quoted_status) {
    item.quoted_status.text =
      item.quoted_status.full_text || item.quoted_status.text;
  }

  if (item.retweeted_status) {
    item.retweeted_status.text =
      item.retweeted_status.full_text || item.retweeted_status.text;
  }

  return item;
};
const prepareTweets = tweets => {
  tweets = map(fullText, tweets);
  tweets = filter(filterTimeline, tweets);
  tweets = groupBy(item => gd(item.created_at), tweets);

  return ungroupInto('weekday', 'tweets')(tweets);
};
const renderVideo = (url) => {
  var regexp = /http(?:s)?:\/\/(?:(www|m)\.)?youtu(?:be\.com\/watch\?v=|\.be\/)([\w\-\_]*)(&(amp;)?[\w\?​=]*)?/gi;
  var matches = regexp.exec(url);

  if (matches) {
    return (
      '<p class="embed-responsive embed-responsive-16by9"><iframe src="//www.youtube.com/embed/' +
      matches[2] +
      '" width="720" height="' +
      720 * (9 / 16) +
      '" class="embed-responsive-item"></iframe></p>'
    );
  }
};

export default {
  d,
  weekday,
  prepareTweets,
  capitalize,
  tweetsUnit,
  getQuotedUser,
  unidecode,
  prevAuthor,
  nextAuthor,
  render: pipe(renderTweet, html, trimTag),
  renderVideo,
  tweetTime, tweetLink,
  getLinks,
};
