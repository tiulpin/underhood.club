import authors from '../authors';
import { accessSync } from 'fs';
import areas from './areas';

const renderedAuthors = authors.filter((author) => {
  try {
    for (const area of areas) {
      accessSync(`dump/${author.username}-${area}.json`);
    }
    return true;
  } catch (err) {
    return false;
  }
});

export default renderedAuthors;
