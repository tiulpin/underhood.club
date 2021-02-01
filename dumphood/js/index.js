import { initate as likely } from 'ilyabirman-likely';

likely();

jQuery(window).on('load resize', () => {
  jQuery('.carousel').carousel({
    pause: true,
    interval: false,
  });

  jQuery('#content').css('paddingBottom', () => {
    return jQuery('#footer').outerHeight();
  });

  jQuery('#footer').css('marginTop', () => {
    return jQuery('#footer').outerHeight() * -1;
  });

  jQuery('.navbar-collapse.collapse').removeClass('collapsing in');

  jQuery('#scroll-spy').each(function () {
    const is_affix = jQuery(this).hasClass('affix');
    const top = jQuery(this).offset().top;
    const bottom = jQuery('#footer').outerHeight();
    const width = jQuery(this).removeClass('affix').width();

    if (is_affix) {
      jQuery(this).addClass('affix');
    }

    jQuery(this)
      .width(width)
      .affix({
        offset: {
          top: top,
          bottom: bottom,
        },
      });
  });

  jQuery(this).trigger('scroll');
});

jQuery(window).on('scroll', () => {
  jQuery('#scroll-spy').each(function () {
    if (jQuery(this).hasClass('affix')) {
      jQuery(this).css('position', '');
    }
  });
});

const d = document; // eslint-disable-line id-length
const $ = d.querySelector.bind(d); // eslint-disable-line id-length

if ($('.js-stats')) {
  require([
    'moment',
    'tablesort',
    'imports?Tablesort=tablesort!tablesort/src/sorts/tablesort.number',
  ], (moment, tablesort) => {
    tablesort($('.host-stats'), { descending: true });

    const lastUpdated = $('.js-last-updated');
    const timestamp = lastUpdated.getAttribute('data-timestamp');
    lastUpdated.textContent = moment.unix(timestamp).locale('ru').fromNow();
  });
}
