import getAuthorArea from './get-author-area';
import authors from './rendered-authors';
import R from 'ramda';

const prev = authorId => (authors[R.inc(R.findIndex(R.propEq('authorId', authorId), authors))] || {}).authorId;
const followers = authorId => getAuthorArea(authorId, 'followers').followersIds || [];

// getDiffFollowers :: String -> Object
export default function getDiffFollowers(authorId) {
  const currentFollowers = followers(authorId);
  const previousFollowers = followers(prev(authorId));

  return {
    gain: R.length(R.difference(currentFollowers, previousFollowers)),
    loss: R.length(R.difference(previousFollowers, currentFollowers)),
  };
}
