import update from "./update-one";

/// Updates every author known in author.js
const updateAuthors = async (authors) => {
  const authorsToUpdate = authors.sort((a, b) => (a.first - b.first));
  for (let index = 0; index < authors.length; index++) {
    update(authors[index], authors[index + 1] && authors[index + 1].first);
  }
}

export default updateAuthors;
