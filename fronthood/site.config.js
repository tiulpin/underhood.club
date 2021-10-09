module.exports = {
  // where it all starts -- the site's root Notion page (required)
  rootNotionPageId: '9bb5775b322849f9bf351821542cdc3b',  // 9b2a9b0a3aee4333af428fec8c9e3620

  // if you want to restrict pages to a single notion workspace (optional)
  // (this should be a Notion ID; see the docs for how to extract this)
  rootNotionSpaceId: null,

  // basic site info (required)
  name: 'underhood.club',
  domain: 'underhood.club',
  author: 'underhood.club, CC BY-SA',

  // open graph metadata (optional)
  description: 'Все твиты коллективных аккаунтов в одном месте',
  socialImage: 'https://underhood.club/og_image.png',
  socialImageTitle: 'underhood.club',
  socialImageSubtitle: '🐦 Архив твитов',

  // social usernames (optional)
  twitter: null,
  github: null,
  linkedin: null,

  // default notion icon and cover images for site-wide consistency (optional)
  // page-specific values will override these site-wide defaults
  defaultPageIcon: 'https://underhood.club/icon.png',
  defaultPageCover: null,
  defaultPageCoverPosition: 0.5,

  // image CDN host to proxy all image requests through (optional)
  // NOTE: this requires you to set up an external image proxy
  imageCDNHost: null,

  // Utteranc.es comments via GitHub issue comments (optional)
  utterancesGitHubRepo: null,

  // whether or not to enable support for LQIP preview images (optional)
  // NOTE: this requires you to set up Google Firebase and add the environment
  // variables specified in .env.example
  isPreviewImageSupportEnabled: false,

  // map of notion page IDs to URL paths (optional)
  // any pages defined here will override their default URL paths
  // example:
  //
  // pageUrlOverrides: {
  //   '/foo': '067dd719a912471ea9a3ac10710e7fdf',
  //   '/bar': '0be6efce9daf42688f65c76b89f8eb27'
  // }
}
