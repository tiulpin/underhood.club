import assert from 'assert';
import { readFileSync } from 'fs-extra';
import cheerio from 'cheerio';
import typeNumbers from 'typographic-numbers';
import { head } from 'ramda';
import authors from './helpers/input-authors';

const latestInfo = head(authors).info;
const numbers = input => typeNumbers(input, { locale: 'ru' });
const make$ = file => cheerio.load(readFileSync(file, { encoding: 'utf8' }));

describe('index page', () => {
  it('short authors info', () => {
    const $ = make$('dist/index.html');
    const pageAuthors = $('.author-list-item');
    const realAuthors = authors.filter(a => a.post !== false);
    assert(pageAuthors.length == realAuthors.length);
  });
  it('don’t have subheading', () => {
    const $ = make$('dist/index.html');
    assert($('.page-header h1 small').length === 0);
  });
  it('followers count exists', () => {
    const $ = make$('dist/index.html');
    const followers = numbers(String(latestInfo.followers_count));
    assert($('.page-header p b').text().indexOf(followers) > 0);
  });
});

describe('stats page', () => {
  it('stats rows', () => {
    const $ = make$('dist/stats/index.html');
    const rows = $('.host-stats__row:not(.host-stats__row_head)');
    assert(rows.length == authors.length);
  });
});

describe('about page', () => {
  it('text', () => {
    const $ = make$('dist/about/index.html');
    assert($('article').text().length > 0);
  });
});

describe('archive pages', () => {
  it('tweets list', () => {
    authors.forEach(function (author) {
      if (author.post === false) return;
      const $ = make$(`dist/${author.username}/index.html`);
      assert($('.tweets .tweet').length > 1);
      assert($('#scroll-spy li').length > 1);
    });
  });
});
