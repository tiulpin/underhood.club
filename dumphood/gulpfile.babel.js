import buildbranch from 'buildbranch';
import rimraf from 'rimraf';
import each from 'each-done';
import express from 'express';
import fs from 'fs-extra';
import { html } from 'commonmark-helpers';
import numbers from 'typographic-numbers';
import numd from 'numd';
import { pipe, prop, head } from 'ramda';
import renderTweet from 'tweet.md';
import autoprefixer from 'autoprefixer';
import pcssImport from 'postcss-import';
import pcssInitial from 'postcss-initial';
import webpack from 'webpack';

import gulp from 'gulp';
import gulpJade from 'gulp-jade';
import rename from 'gulp-rename';
import { log, PluginError } from 'gulp-util';
import jimp from 'gulp-jimp';
import postcss from 'gulp-postcss';

import articleData from 'article-data';
import getStats from './helpers/stats.js';
import webpackConfig from './webpack.config.babel.js';

import authorRender from './helpers/author-render';
import bust from './helpers/bust';
import lastUpdated from './helpers/last-updated';
import { site, underhood, github, curator } from './underhood';
import replaceMd from './helpers/replace-md';

import authors from './helpers/input-authors';
const latestInfo = head(authors).info;

const jadeDefaults = {
  pretty: true,
  locals: {
    site,
    latestInfo,
    underhood,
    github,
    curator,
    numbers: (input) => numbers(input, { locale: 'ru' }),
    people: numd('человек', 'человека', 'человек'),
  },
};

const getOptions = (opts = {}) =>
  Object.assign({}, jadeDefaults, opts, {
    locals: Object.assign({}, jadeDefaults.locals, opts.locals),
  });

const jade = (opts) => gulpJade(getOptions(opts));
const firstTweet = pipe(prop('tweets'), head);
const render = pipe(renderTweet, html);

/**
 * MAIN TASKS
 */

const css = () =>
  gulp
    .src('css/styles.css')
    .pipe(postcss([pcssImport, pcssInitial, autoprefixer]))
    .pipe(gulp.dest('dist/css'));

const index = () => {
  const authorsToPost = authors.filter((author) => author.post !== false);
  return gulp
    .src('layouts/index.jade')
    .pipe(
      jade({
        locals: {
          title: site.title,
          desc: site.description,
          currentAuthor: head(authors),
          authors: authorsToPost,
          helpers: { authorRender, bust },
        },
      })
    )
    .pipe(rename({ basename: 'index' }))
    .pipe(gulp.dest('dist'));
};

const stats = () => {
  const currentAuthor = head(authors.filter((author) => author.post === false));
  return gulp
    .src('layouts/stats.jade')
    .pipe(
      jade({
        locals: {
          title: `Статистика @${site.title}`,
          url: 'stats/',
          desc: site.description,
          lastUpdated,
          stats: getStats(authors),
          currentAuthor: currentAuthor,
          helpers: { bust },
        },
      })
    )
    .pipe(rename({ dirname: 'stats' }))
    .pipe(rename({ basename: 'index' }))
    .pipe(gulp.dest('dist'));
};

const about = () => {
  let readme = fs.readFileSync('./pages/about.md', { encoding: 'utf8' });
  readme = replaceMd(readme);
  const article = articleData(readme, 'D MMMM YYYY', 'ru');
  return gulp
    .src('layouts/article.jade')
    .pipe(
      jade({
        locals: Object.assign({}, article, {
          title: 'О проекте',
          url: 'about/',
          helpers: { bust },
        }),
      })
    )
    .pipe(rename({ dirname: 'about' }))
    .pipe(rename({ basename: 'index' }))
    .pipe(gulp.dest('dist'));
};

const forAuthors = () => {
  let readme = fs.readFileSync('./pages/authoring.md', { encoding: 'utf8' });
  readme = replaceMd(readme);
  const article = articleData(readme, 'D MMMM YYYY', 'ru');
  return gulp
    .src('layouts/article.jade')
    .pipe(
      jade({
        locals: Object.assign({}, article, {
          title: 'Авторам',
          url: 'authoring/',
          helpers: { bust },
        }),
      })
    )
    .pipe(rename({ dirname: 'authoring' }))
    .pipe(rename({ basename: 'index' }))
    .pipe(gulp.dest('dist'));
};

const instruction = () => {
  let readme = fs.readFileSync('./pages/instruction.md', { encoding: 'utf8' });
  readme = replaceMd(readme);
  const article = articleData(readme, 'D MMMM YYYY', 'ru');
  return gulp
    .src('layouts/article.jade')
    .pipe(
      jade({
        locals: Object.assign({}, article, {
          title: 'Автору',
          url: 'instruction/',
          helpers: { bust },
        }),
      })
    )
    .pipe(rename({ dirname: 'instruction' }))
    .pipe(rename({ basename: 'index' }))
    .pipe(gulp.dest('dist'));
};

const authorsArchives = (done) => {
  const authorsToPost = authors.filter((author) => author.post !== false);
  each(
    authorsToPost,
    (author) => {
      return gulp
        .src('./layouts/author.jade')
        .pipe(
          jade({
            pretty: true,
            locals: {
              title: `Неделя @${author.username} в @${site.title}`,
              author,
              helpers: { authorRender, bust },
            },
          })
        )
        .pipe(rename({ dirname: author.authorId }))
        .pipe(rename({ basename: 'index' }))
        .pipe(gulp.dest('dist'));
    },
    done
  );
};

const userpics = () =>
  gulp
    .src('dump/images/*-image*')
    .pipe(jimp({ '': { resize: { width: 192, height: 192 } } }))
    .pipe(gulp.dest('dist/images'));

const banners = () =>
  gulp.src('dump/images/*-banner*').pipe(gulp.dest('dist/images'));

const currentUserpic = () =>
  gulp
    .src(`dump/images/${head(authors).authorId}-image*`)
    .pipe(jimp({ '': { resize: { width: 192, height: 192 } } }))
    .pipe(rename('current-image'))
    .pipe(gulp.dest('dist/images'));

const currentBanner = () =>
  gulp
    .src(`dump/images/${head(authors).authorId}-banner*`)
    .pipe(rename('current-banner'))
    .pipe(gulp.dest('dist/images'));

const currentMedia = gulp.series(currentUserpic, currentBanner);

const js = (done) => {
  webpack(webpackConfig, (err, stats) => {
    if (err) throw new PluginError('webpack', err);
    done();
  });
};

const staticPages = () =>
  gulp
    .src(['static/**', 'static/.**', 'node_modules/bootstrap/dist/**'])
    .pipe(gulp.dest('dist'));

const server = () => {
  const app = express();
  app.use(express.static('dist'));
  app.listen(4000);
  log('Server is running on http://localhost:4000');
};

/**
 * FLOW
 */
const htmlPages = gulp.series(
  stats,
  gulp.parallel(authorsArchives, index, about, forAuthors, instruction)
);

const build = gulp.series(
  css,
  js,
  staticPages,
  htmlPages,
  userpics,
  banners,
  currentMedia
);

const watchers = () => {
  gulp.watch(['**/*.jade'], gulp.series(css, htmlPages));
  gulp.watch(['css/**/*.css'], css);
  gulp.watch('js/**/*.js', js);
  gulp.watch('pages/**/*.md', gulp.parallel(about, forAuthors, instruction));
  gulp.watch('static/**', staticPages);
};

const watch = gulp.parallel(server, gulp.series(build, watchers));

const clean = (done) => rimraf('dist', done);

exports.clean = clean;

exports.build = build;

exports.deploy = gulp.series(build, (done) =>
  buildbranch({ branch: 'gh-pages', folder: 'dist' }, done)
);

exports.default = gulp.series(clean, watch);
