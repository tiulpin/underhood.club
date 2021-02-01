import { map, merge } from 'ramda';
import authors from './rendered-authors';
import getAuthorArea from './get-author-area';

const saturate = (author) =>
  merge(author, {
    info: getAuthorArea(author.authorId, 'info') || {},
    tweets: getAuthorArea(author.authorId, 'tweets').tweets || [],
    media: merge(
      { image: '', banner: '' },
      getAuthorArea(author.authorId, 'media')
    ),
  });

export default map(saturate, authors);
