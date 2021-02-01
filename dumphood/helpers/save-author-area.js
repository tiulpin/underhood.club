import { outputJSON } from 'fs-extra';

const spaces = 2;

export default function saveAuthorArea(username, area, content) {
  outputJSON(`./dump/${username}-${area}.json`, content, { spaces }, err => {
    console.log(`${err ? '✗' : '✓'} ${username}’s ${area}`);
  });
}
