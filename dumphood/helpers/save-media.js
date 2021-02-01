import save from './save';
import profileMedia from 'twitter-profile-media';

const saveMedia = (tokens, underhood, username, cb) => {
  profileMedia(tokens, underhood, (err, res) => {
    if (err) return cb(err);
    const { image: imageURL, banner: bannerURL } = res
    save(imageURL, `./images/${username}-image`, (err, image) => {
      if (err) return cb(err);
      if (!bannerURL) { return cb(null, { image }) }
      save(bannerURL, `./images/${username}-banner`, (err, banner) => {
        if (err) return cb(err);
        cb(null, { image, banner });
      });
    });
  });
};

export default saveMedia;
