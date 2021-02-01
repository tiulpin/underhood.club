import Twitter from 'twit';
import { merge, flatten } from 'ramda';

function accumulate(get, options, followersIds, tokens, cb) {
  get(options, (err, { ids, next_cursor_str: cursor } = res) => {
    if (err) return cb(err);
    const accumulatedFollowersIds = [...followersIds, ...ids];

    if (cursor === '0') {
      const result = flatten(accumulatedFollowersIds);
      cb(null, result);
      return;
    }

    return accumulate(get, merge(options, { cursor }), accumulatedFollowersIds, tokens, cb);
  });
}

export default function getTwitterFollowers(tokens, username, cb) {
  const client = new Twitter(tokens);
  const get = client.get.bind(client, 'followers/ids');
  const options = { screen_name: username, stringify_ids: true, count: 5000 };
  return accumulate(get, options, [], tokens, cb);
};
