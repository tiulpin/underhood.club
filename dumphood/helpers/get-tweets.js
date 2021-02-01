import Twitter from 'twit';
import dec from 'bignum-dec';
import { merge, pipe, prop, last, concat, isEmpty } from 'ramda';

const defaults = {
  count: 200,
  trim_user: true,
  include_rts: true,
  exclude_replies: false,
  tweet_mode: 'extended',
};

const getNextOptions = (options, tweets) =>
  (isEmpty(tweets))
    ? options
    : merge(options, { max_id: pipe(last, prop('id_str'), dec)(tweets) });

function accumulate(get, options, tweets, cb) {
  const nextOptions = getNextOptions(options, tweets);

  if (nextOptions.max_id === nextOptions.since_id) {
    cb(null, tweets);
    return;
  }

  get(nextOptions, (err, res) => {
    if (err) {
      return cb(err);
    }
    const accumulatedTweets = concat(tweets, res);

    return (isEmpty(res))
      ? cb(null, accumulatedTweets)
      : accumulate(get, nextOptions, accumulatedTweets, cb);
  });
}

export default function getTweets(tokens, username, sinceId, maxId, cb) {
  const client = new Twitter(tokens);
  const get = client.get.bind(client, 'statuses/user_timeline');
  const options = merge(merge(defaults, { screen_name: username, since_id: sinceId }), maxId && { max_id: maxId });
  return accumulate(get, options, [], cb);
};
