import { readJsonSync, outputJSON } from 'fs-extra';

import authorId from '../../helpers/author-id';

const authors = authorId([
  // Insert authors to migrate
]);

export default function (area, fromFolder, toFolder, handler) {
  authors.forEach((author) => {
    try {
      let content = readJsonSync(
        `./${fromFolder}/${author.authorId}-${area}.json`
      );
      const fixed = handler(content);

      outputJSON(
        `./${toFolder}/${author.authorId}-${area}.json`,
        fixed,
        { spaces: 2 },
        (err) => {
          console.log(`${err ? '✗' : '✓'} ${author.authorId}’`);
        }
      );
    } catch (err) {
      console.log(err);
    }
  });
}
