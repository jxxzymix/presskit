'use strict';

const $ = (selector, root = document) => root?.querySelector(selector) ?? null;
const $$ = (selector, root = document) => root ? [...root.querySelectorAll(selector)] : [];
const motionPreference = window.matchMedia('(prefers-reduced-motion: reduce)');
let reduceMotion = motionPreference.matches;

function initIntro() {
  const intro = $('#intro');
  if (!intro) return;
  const delay = reduceMotion ? 0 : 1550;
  window.setTimeout(() => {
    intro.classList.add('is-hidden');
  }, delay);
}

function initNavigation() {
  const toggle = $('#mobileToggle');
  const menu = $('#mobileMenu');
  const mobileBrand = $('.mobile-brand');
  const desktopNav = $('.desktop-nav');
  const backToTop = $('#backToTop');
  const pageInertTargets = [$('#main'), $('.site-footer'), backToTop].filter(Boolean);
  const setMenu = open => {
    if (!toggle || !menu) return;
    toggle.classList.toggle('open', open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Tutup menu' : 'Buka menu');
    menu.classList.toggle('open', open);
    menu.setAttribute('aria-hidden', String(!open));
    menu.inert = !open;
    pageInertTargets.forEach(item => { item.inert = open; });
    document.body.classList.toggle('menu-open', open);
    if (open) window.requestAnimationFrame(() => $('.mobile-nav-links a', menu)?.focus({ preventScroll: true }));
  };
  setMenu(false);
  toggle?.addEventListener('click', () => setMenu(!menu.classList.contains('open')));
  mobileBrand?.addEventListener('click', () => setMenu(false));
  if (menu) $$('a', menu).forEach(link => link.addEventListener('click', () => {
    const target = link.hash ? $(link.hash) : null;
    setMenu(false);
    if (target) window.requestAnimationFrame(() => {
      target.setAttribute('tabindex', '-1');
      target.focus({ preventScroll: true });
    });
  }));
  document.addEventListener('keydown', event => {
    if (!menu?.classList.contains('open')) return;
    if (event.key === 'Escape') {
      setMenu(false);
      toggle?.focus();
      return;
    }
    if (event.key !== 'Tab' || !toggle) return;
    const controls = [toggle, ...$$('a[href], button:not([disabled]):not([hidden])', menu)]
      .filter(item => item.getClientRects().length);
    if (!controls.length) return;
    const first = controls[0];
    const firstMenuControl = controls[1] || first;
    const last = controls[controls.length - 1];
    const active = document.activeElement;
    if (!event.shiftKey && active === toggle) {
      event.preventDefault();
      firstMenuControl.focus();
    } else if (!event.shiftKey && active === last) {
      event.preventDefault();
      first.focus();
    } else if (event.shiftKey && active === first) {
      event.preventDefault();
      last.focus();
    } else if (!controls.includes(active)) {
      event.preventDefault();
      (event.shiftKey ? last : firstMenuControl).focus();
    }
  });

  const menuBreakpoint = window.matchMedia('(max-width: 920px)');
  const resetMenuAtDesktop = event => {
    if (event.matches || !menu?.classList.contains('open')) return;
    const focusWasInMobileNav = document.activeElement === toggle || menu.contains(document.activeElement);
    setMenu(false);
    if (focusWasInMobileNav) $('.brand')?.focus({ preventScroll: true });
  };
  if (menuBreakpoint.addEventListener) menuBreakpoint.addEventListener('change', resetMenuAtDesktop);
  else menuBreakpoint.addListener(resetMenuAtDesktop);

  const links = $$('.side-nav a, #mobileMenu .mobile-nav-links a');
  const sections = $$('main section[id]');
  const setActiveLink = hash => links.forEach(link => {
    const active = link.hash === hash;
    link.classList.toggle('active', active);
    if (active) link.setAttribute('aria-current', 'location'); else link.removeAttribute('aria-current');
  });
  links.forEach(link => link.addEventListener('click', () => setActiveLink(link.hash)));
  if ('IntersectionObserver' in window && links.length) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        setActiveLink(`#${entry.target.id}`);
      });
    }, { rootMargin: '-42% 0px -52% 0px' });
    sections.forEach(section => observer.observe(section));
  }

  const progress = $('.scroll-progress i');
  const updateProgress = () => {
    if (!progress) return;
    const maximum = document.documentElement.scrollHeight - window.innerHeight;
    const ratio = maximum > 0 ? Math.min(1, Math.max(0, window.scrollY / maximum)) : 0;
    progress.style.height = `${ratio * 100}%`;
    desktopNav?.classList.toggle('is-scrolled', window.scrollY > 36);
    if (backToTop) {
      const visible = window.scrollY > window.innerHeight * .65;
      backToTop.classList.toggle('is-visible', visible);
      backToTop.setAttribute('aria-hidden', String(!visible));
      backToTop.tabIndex = visible ? 0 : -1;
      backToTop.style.setProperty('--page-progress', `${ratio * 360}deg`);
    }
  };
  window.addEventListener('scroll', updateProgress, { passive: true });
  window.addEventListener('resize', updateProgress, { passive: true });
  backToTop?.addEventListener('click', () => {
    const home = $('#home');
    home?.setAttribute('tabindex', '-1');
    home?.focus({ preventScroll: true });
    window.scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' });
  });
  updateProgress();
}

function initReveal() {
  const items = $$('[data-reveal]');
  if (!items.length) return;
  if (reduceMotion || !('IntersectionObserver' in window)) {
    items.forEach(item => item.classList.add('is-visible'));
    return;
  }
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('is-visible');
      observer.unobserve(entry.target);
    });
  }, { threshold: .08, rootMargin: '0px 0px -7% 0px' });
  items.forEach(item => observer.observe(item));
}

function initWallpaper() {
  const videos = $$('[data-wallpaper-video]');
  const video = $('#wallpaperVideo') || videos[0];
  const layer = $('.wallpaper');
  const toggles = $$('.wallpaper-toggle');
  const viewportVideos = videos.filter(item => item.hasAttribute('data-viewport-motion'));
  const visibleViewportVideos = new WeakSet();
  let requestedPaused = false;
  const activeAtViewport = item => {
    if (item.classList.contains('brand-motion')) {
      return item.closest('.desktop-nav') ? window.innerWidth > 920 : window.innerWidth <= 920;
    }
    if (item.hasAttribute('data-viewport-motion')) return visibleViewportVideos.has(item);
    return true;
  };
  if (!video || !toggles.length) return;
  const motionHost = item => {
    if (item.classList.contains('brand-motion')) return item.closest('.brand, .mobile-brand');
    if (item.classList.contains('snapshot-mark-motion')) return item.closest('.snapshot-mark');
    return null;
  };
  videos.forEach(item => {
    const host = motionHost(item);
    if (!host) return;
    item.addEventListener('playing', () => {
      host.classList.add('is-playing');
      host.classList.remove('is-failed');
    });
    ['pause', 'emptied'].forEach(type => item.addEventListener(type, () => host.classList.remove('is-playing')));
    item.addEventListener('error', () => {
      host.classList.remove('is-playing');
      host.classList.add('is-failed');
    });
  });
  const syncControls = paused => {
    layer?.classList.toggle('is-paused', paused);
    document.documentElement.classList.toggle('visuals-paused', paused);
    toggles.forEach(toggle => {
      toggle.setAttribute('aria-pressed', String(paused));
      const label = $('span', toggle);
      if (label) label.textContent = paused ? 'Play visual' : 'Pause visual';
    });
  };
  const syncPlayback = () => {
    videos.forEach(item => {
      const shouldPause = reduceMotion || requestedPaused || !activeAtViewport(item);
      if (shouldPause) item.pause(); else item.play().catch(() => {});
    });
  };
  const setPaused = paused => {
    requestedPaused = paused;
    syncPlayback();
    syncControls(paused);
  };
  if ('IntersectionObserver' in window && viewportVideos.length) {
    const viewportObserver = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) visibleViewportVideos.add(entry.target);
        else visibleViewportVideos.delete(entry.target);
      });
      syncPlayback();
    }, { threshold: .01, rootMargin: '220px 0px' });
    viewportVideos.forEach(item => viewportObserver.observe(item));
  } else {
    viewportVideos.forEach(item => visibleViewportVideos.add(item));
  }
  const applyMotionPreference = (reloadSources = false) => {
    if (reduceMotion) {
      videos.forEach(item => {
        item.pause();
        if (reloadSources) item.load();
      });
      toggles.forEach(toggle => { toggle.hidden = true; });
      $('#intro')?.classList.add('is-hidden');
      $$('[data-reveal]').forEach(item => item.classList.add('is-visible'));
      syncControls(true);
      return;
    }
    toggles.forEach(toggle => { toggle.hidden = false; });
    if (reloadSources) videos.forEach(item => item.load());
    window.requestAnimationFrame(() => {
      syncPlayback();
      syncControls(requestedPaused);
    });
  };
  toggles.forEach(toggle => toggle.addEventListener('click', () => {
    const currentlyPaused = document.documentElement.classList.contains('visuals-paused');
    setPaused(!currentlyPaused);
  }));
  video.addEventListener('error', () => {
    layer?.classList.add('is-paused');
  });
  const breakpoint = window.matchMedia('(max-width: 920px)');
  let reloadTimer;
  const onBreakpointChange = () => {
    const wasPaused = requestedPaused;
    window.clearTimeout(reloadTimer);
    reloadTimer = window.setTimeout(() => {
      videos.forEach(item => item.load());
      if (!reduceMotion) window.requestAnimationFrame(() => setPaused(wasPaused));
    }, 80);
  };
  if (breakpoint.addEventListener) breakpoint.addEventListener('change', onBreakpointChange);
  else breakpoint.addListener(onBreakpointChange);
  const onMotionPreferenceChange = event => {
    reduceMotion = event.matches;
    applyMotionPreference(true);
  };
  if (motionPreference.addEventListener) motionPreference.addEventListener('change', onMotionPreferenceChange);
  else motionPreference.addListener(onMotionPreferenceChange);
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) return;
    syncPlayback();
    syncControls(reduceMotion || requestedPaused);
  });
  applyMotionPreference();
}

function initJourney() {
  const buttons = $$('.journey button');
  const detail = $('#journeyDetail');
  buttons.forEach(button => button.setAttribute('aria-pressed', String(button.classList.contains('active'))));
  buttons.forEach(button => button.addEventListener('click', () => {
    buttons.forEach(item => {
      const active = item === button;
      item.classList.toggle('active', active);
      item.setAttribute('aria-pressed', String(active));
    });
    if (detail) detail.innerHTML = `<strong>${button.dataset.stage}</strong> — ${button.dataset.detail}`;
  }));
}

function initLightbox() {
  const dialog = $('#lightbox');
  if (!dialog) return;
  const placeholder = $('img', dialog)?.getAttribute('src') || '';
  $$('[data-lightbox]').forEach(button => button.addEventListener('click', () => {
    const image = $('img', dialog);
    const caption = $('p', dialog);
    image.src = button.dataset.lightbox;
    image.alt = button.dataset.alt || '';
    caption.textContent = button.dataset.alt || '';
    document.body.classList.add('dialog-open');
    dialog.showModal();
  }));
  $('[data-close-lightbox]', dialog)?.addEventListener('click', () => dialog.close());
  dialog.addEventListener('close', () => {
    document.body.classList.remove('dialog-open');
    const image = $('img', dialog);
    if (!image) return;
    image.src = placeholder;
    image.alt = '';
  });
  dialog.addEventListener('click', event => {
    if (event.target === dialog) dialog.close();
  });
}

function initMediaPlayer() {
  const links = $$([
    '.soundcloud-tracks a[href*="soundcloud.com/"]',
    '.set-list li a[href*="youtube.com/"]',
    '.epk-soundcloud-grid a[href*="soundcloud.com/"]',
    '.epk-youtube-grid a[href*="youtube.com/"]'
  ].join(','));
  if (!links.length || typeof HTMLDialogElement === 'undefined') return;

  const dialog = document.createElement('dialog');
  dialog.className = 'media-player';
  dialog.setAttribute('aria-labelledby', 'mediaPlayerTitle');
  dialog.innerHTML = `
    <div class="media-player-shell">
      <button class="media-player-close" type="button" aria-label="Tutup player">×</button>
      <header><small id="mediaPlayerPlatform">INLINE PLAYER</small><h2 id="mediaPlayerTitle">JXXZY</h2></header>
      <div class="media-player-frame"></div>
      <footer><span>Playing inside JXXZY Press Kit</span><a href="https://soundcloud.com/jxxzyshn" target="_blank" rel="noreferrer">Open original ↗</a></footer>
    </div>`;
  document.body.append(dialog);

  const frame = $('.media-player-frame', dialog);
  const platform = $('#mediaPlayerPlatform', dialog);
  const title = $('#mediaPlayerTitle', dialog);
  const original = $('footer a', dialog);
  const clearPlayer = () => {
    if (frame) frame.replaceChildren();
    frame?.classList.remove('is-soundcloud', 'is-youtube');
  };
  const closePlayer = () => {
    clearPlayer();
    if (dialog.open) dialog.close();
  };
  $('.media-player-close', dialog)?.addEventListener('click', closePlayer);
  dialog.addEventListener('close', clearPlayer);
  dialog.addEventListener('close', () => document.body.classList.remove('dialog-open'));
  dialog.addEventListener('click', event => {
    const box = dialog.getBoundingClientRect();
    const outside = event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom;
    if (outside) closePlayer();
  });

  links.forEach(link => {
    link.setAttribute('aria-haspopup', 'dialog');
    link.addEventListener('click', event => {
      if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      const url = new URL(link.href);
      const isSoundCloud = url.hostname.includes('soundcloud.com');
      const videoId = url.searchParams.get('v');
      if (!isSoundCloud && !videoId) return;
      event.preventDefault();
      clearPlayer();

      const mediaTitle = $('strong', link)?.textContent?.trim() || 'JXXZY';
      const iframe = document.createElement('iframe');
      iframe.title = `${mediaTitle} — ${isSoundCloud ? 'SoundCloud' : 'YouTube'} player`;
      iframe.allow = isSoundCloud
        ? 'autoplay; encrypted-media'
        : 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
      iframe.referrerPolicy = 'strict-origin-when-cross-origin';
      iframe.allowFullscreen = !isSoundCloud;

      if (isSoundCloud) {
        const params = new URLSearchParams({
          url: link.href,
          color: '#17b7e8',
          auto_play: 'true',
          hide_related: 'true',
          show_comments: 'false',
          show_user: 'true',
          show_reposts: 'false',
          show_teaser: 'false',
          visual: 'true'
        });
        iframe.src = `https://w.soundcloud.com/player/?${params}`;
        frame?.classList.add('is-soundcloud');
        if (platform) platform.textContent = 'SOUNDCLOUD / PLAY HERE';
      } else {
        iframe.src = `https://www.youtube-nocookie.com/embed/${encodeURIComponent(videoId)}?autoplay=1&rel=0`;
        frame?.classList.add('is-youtube');
        if (platform) platform.textContent = 'YOUTUBE / PLAY HERE';
      }

      if (title) title.textContent = mediaTitle;
      if (original) {
        original.href = link.href;
        original.textContent = `Open on ${isSoundCloud ? 'SoundCloud' : 'YouTube'} ↗`;
      }
      frame?.append(iframe);
      document.body.classList.add('dialog-open');
      dialog.showModal();
    });
  });
}

async function copyText(text) {
  if (navigator.clipboard?.writeText) {
    try {
      await navigator.clipboard.writeText(text);
      return;
    } catch (_) {}
  }
  const field = document.createElement('textarea');
  field.value = text;
  field.style.position = 'fixed';
  field.style.opacity = '0';
  document.body.append(field);
  field.select();
  const copied = document.execCommand('copy');
  field.remove();
  if (!copied) throw new Error('Copy command failed');
}

function initCopyButtons() {
  $$('[data-copy-target]').forEach(button => {
    button.setAttribute('aria-live', 'polite');
    button.addEventListener('click', async () => {
    const target = document.getElementById(button.dataset.copyTarget);
    if (!target) return;
    const original = button.textContent;
    try {
      await copyText(target.innerText.trim());
      button.textContent = 'Copied';
    } catch (_) {
      button.textContent = 'Select text';
    }
    window.setTimeout(() => { button.textContent = original; }, 1600);
    });
  });
}

function bookingBrief(form) {
  const data = Object.fromEntries(new FormData(form));
  return [
    'BOOKING / COLLABORATION — JXXZY',
    '',
    `Event: ${data.event || '-'}`,
    `Date: ${data.date || '-'}`,
    `City: ${data.city || '-'}`,
    `Venue: ${data.venue || '-'}`,
    `Set time: ${data.settime || '-'}`,
    `Set duration: ${data.duration || '-'}`,
    `Expected capacity: ${data.capacity || '-'}`,
    `Artist lineup: ${data.lineup || '-'}`,
    `DJ equipment: ${data.equipment || '-'}`,
    `Transport & accommodation: ${data.logistics || '-'}`,
    `PIC / promoter: ${data.contact || '-'}`,
    `WhatsApp: ${data.whatsapp || '-'}`,
    `Email: ${data.email || '-'}`,
    `Notes: ${data.notes || '-'}`,
    '',
    'Sent from JXXZY Official Press Kit 2026.'
  ].join('\n');
}

function initBooking() {
  const section = $('#booking');
  const form = $('#bookingForm');
  const status = $('#formStatus');
  const setStatus = (message = '', type = '') => {
    if (!status) return;
    status.textContent = message;
    status.classList.toggle('is-error', type === 'error');
    status.classList.toggle('is-success', type === 'success');
  };
  $('[data-js-submit]', form)?.removeAttribute('disabled');
  $$('.booking-open').forEach(button => button.addEventListener('click', () => {
    section?.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth' });
    window.setTimeout(() => $('[name="event"]', form)?.focus({ preventScroll: true }), reduceMotion ? 0 : 650);
  }));
  if (!form) return;
  form.addEventListener('input', () => setStatus());
  form.addEventListener('invalid', () => {
    setStatus('Lengkapi field wajib sebelum mengirim event brief.', 'error');
  }, true);
  const valid = () => {
    const result = form.reportValidity();
    if (!result) setStatus('Lengkapi field wajib sebelum mengirim event brief.', 'error');
    return result;
  };
  form.addEventListener('submit', event => {
    event.preventDefault();
    if (!valid()) return;
    const url = `https://wa.me/6285892904834?text=${encodeURIComponent(bookingBrief(form))}`;
    const opened = window.open('about:blank', '_blank');
    if (opened) {
      opened.opener = null;
      opened.location.replace(url);
      setStatus('WhatsApp dibuka dengan event brief.', 'success');
    } else {
      window.location.href = url;
    }
  });
  $('#bookingEmail')?.addEventListener('click', () => {
    if (!valid()) return;
    const eventName = new FormData(form).get('event') || 'Event';
    window.location.href = `mailto:jxxzyshn@gmail.com?subject=${encodeURIComponent(`Booking JXXZY — ${eventName}`)}&body=${encodeURIComponent(bookingBrief(form))}`;
    setStatus('Aplikasi email dibuka dengan event brief.', 'success');
  });
}

function initPrint() {
  const documentRoot = $('#epkDocument');
  const images = $$('img', documentRoot);
  if (document.body.classList.contains('epk-standalone')) images.forEach(image => { image.loading = 'eager'; });
  $$('[data-print]').forEach(button => button.addEventListener('click', async () => {
    const original = button.textContent;
    button.disabled = true;
    button.textContent = 'Preparing media…';
    try {
      images.forEach(image => { image.loading = 'eager'; });
      const mediaReady = Promise.all(images.map(image => {
        if (image.complete) return image.decode?.().catch(() => {}) || Promise.resolve();
        return new Promise(resolve => {
          image.addEventListener('load', resolve, { once: true });
          image.addEventListener('error', resolve, { once: true });
        });
      }));
      await Promise.race([
        Promise.all([mediaReady, document.fonts?.ready || Promise.resolve()]),
        new Promise(resolve => window.setTimeout(resolve, 8000))
      ]);
      window.print();
    } finally {
      button.disabled = false;
      button.textContent = original;
    }
  }));
}

initIntro();
initNavigation();
initReveal();
initWallpaper();
initJourney();
initLightbox();
initMediaPlayer();
initCopyButtons();
initBooking();
initPrint();
