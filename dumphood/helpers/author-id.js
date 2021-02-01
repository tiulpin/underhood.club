import R from 'ramda';

const filterUsernames = (username, acc) => {
  return R.filter(R.propEq('username', username), acc);
};

const reduceAuthorId = (acc, author) => {
  const username = author.username;
  const times = R.length(filterUsernames(username, acc));
  const authorId = times > 0 ? `${username}-${R.inc(times)}` : username;

  return R.prepend(R.assoc('authorId', authorId, author), acc);
};

/// Repeated authors will have authorId with suffix -2,-3,-4 for new appearances on twitter.
// authorId :: [a] -> [b]
export default R.reduceRight(reduceAuthorId, []);
