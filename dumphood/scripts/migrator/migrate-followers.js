import fixer from "./fixer";

fixer('followers', 'dump-old', 'dump-old', (content) => {
  return {
    followersIds: content.followers.map(user => user.id_str)
  }
});
