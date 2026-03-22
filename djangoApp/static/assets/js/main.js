/**
 * MARKETPLACE — main.js
 * Handles: navbar scroll, mobile drawer, search, cart badge,
 * alert dismiss, lazy-load images, intersection observer reveals.
 */

'use strict';

/* ── Helpers ────────────────────────────────────────────────── */
const $ = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

/* ── Navbar: scroll shadow ──────────────────────────────────── */
(function initNavbarScroll() {
  const navbar = $('.navbar');
  if (!navbar) return;

  const toggle = () => navbar.classList.toggle('scrolled', window.scrollY > 10);
  window.addEventListener('scroll', toggle, { passive: true });
  toggle();
})();

/* ── Navbar: mobile hamburger / drawer ──────────────────────── */
(function initMobileNav() {
  const hamburger = $('.navbar__hamburger');
  const drawer    = $('.navbar__drawer');
  if (!hamburger || !drawer) return;

  let open = false;

  hamburger.addEventListener('click', () => {
    open = !open;
    hamburger.classList.toggle('open', open);
    drawer.classList.toggle('open', open);
    hamburger.setAttribute('aria-expanded', open);
    document.body.style.overflow = open ? 'hidden' : '';
  });

  // Close on outside click
  document.addEventListener('click', (e) => {
    if (open && !hamburger.contains(e.target) && !drawer.contains(e.target)) {
      open = false;
      hamburger.classList.remove('open');
      drawer.classList.remove('open');
      document.body.style.overflow = '';
    }
  });
})();

/* ── Search: expand on focus (mobile) ─────────────────────── */
(function initSearch() {
  const input = $('.navbar__search-input');
  if (!input) return;

  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      const q = input.value.trim();
      if (q) {
        const url = new URL(window.location.href);
        url.searchParams.set('q', q);
        // In Django this would navigate to the search results page:
        // window.location.href = `/search/?q=${encodeURIComponent(q)}`;
        console.log('Search:', q);
      }
    }
    if (e.key === 'Escape') input.blur();
  });
})();

/* ── Cart badge: animate on update ─────────────────────────── */
const Cart = {
  badge: null,

  init() {
    this.badge = $('.cart-badge');
    this.updateCount();
  },

  getCount() {
    try {
      return parseInt(sessionStorage.getItem('cart_count') || '0', 10);
    } catch { return 0; }
  },

  setCount(n) {
    try { sessionStorage.setItem('cart_count', String(n)); } catch {}
    this.updateCount();
  },

  updateCount() {
    if (!this.badge) return;
    const n = this.getCount();
    this.badge.textContent = n > 99 ? '99+' : n;
    this.badge.hidden = n === 0;
  },

  bump() {
    this.setCount(this.getCount() + 1);
    if (!this.badge) return;
    this.badge.classList.remove('pop');
    void this.badge.offsetWidth; // reflow
    this.badge.classList.add('pop');
  }
};

/* ── Alert / message dismiss ────────────────────────────────── */
(function initAlerts() {
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('.alert__close');
    if (!btn) return;
    const alert = btn.closest('.alert');
    if (!alert) return;
    alert.style.transition = 'opacity 0.2s ease, transform 0.2s ease';
    alert.style.opacity = '0';
    alert.style.transform = 'translateX(8px)';
    setTimeout(() => alert.remove(), 220);
  });

  // Auto-dismiss success alerts after 5 s
  $$('.alert--success').forEach((el) => {
    setTimeout(() => {
      if (!el.isConnected) return;
      el.style.transition = 'opacity 0.5s ease';
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 520);
    }, 5000);
  });
})();

/* ── "Add to cart" buttons ──────────────────────────────────── */
(function initAddToCart() {
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-add-to-cart]');
    if (!btn) return;

    // Visual feedback
    const original = btn.innerHTML;
    btn.innerHTML = '✓ Added';
    btn.style.background = 'var(--clr-success)';
    btn.disabled = true;

    setTimeout(() => {
      btn.innerHTML = original;
      btn.style.background = '';
      btn.disabled = false;
    }, 1800);

    Cart.bump();
  });
})();

/* ── Intersection Observer: fade-up reveals ─────────────────── */
(function initReveal() {
  const els = $$('[data-reveal]');
  if (!els.length) return;

  const io = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('fade-up');
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  els.forEach((el) => io.observe(el));
})();

/* ── Category pills: active toggle ─────────────────────────── */
(function initCategoryPills() {
  const container = $('.categories');
  if (!container) return;

  container.addEventListener('click', (e) => {
    const pill = e.target.closest('.category-pill');
    if (!pill) return;
    $$('.category-pill', container).forEach(p => p.classList.remove('active'));
    pill.classList.add('active');
  });
})();

/* ── Lazy-load images ───────────────────────────────────────── */
(function initLazyImages() {
  if (!('IntersectionObserver' in window)) return;

  const io = new IntersectionObserver((entries, obs) => {
    entries.forEach(({ isIntersecting, target }) => {
      if (!isIntersecting) return;
      const src = target.dataset.src;
      if (src) {
        target.src = src;
        target.removeAttribute('data-src');
      }
      obs.unobserve(target);
    });
  }, { rootMargin: '200px' });

  $$('img[data-src]').forEach(img => io.observe(img));
})();

/* ── Tooltip: simple title-based ───────────────────────────── */
(function initTooltips() {
  let tip = null;

  const show = (el, text) => {
    tip = document.createElement('div');
    tip.className = 'tooltip';
    tip.textContent = text;
    Object.assign(tip.style, {
      position: 'fixed',
      background: 'var(--clr-nav-bg)',
      color: 'var(--clr-nav-text)',
      fontSize: '0.75rem',
      padding: '4px 10px',
      borderRadius: '4px',
      pointerEvents: 'none',
      zIndex: '9999',
      whiteSpace: 'nowrap',
      boxShadow: '0 2px 8px rgba(0,0,0,.25)',
    });
    document.body.appendChild(tip);

    const r = el.getBoundingClientRect();
    tip.style.left = `${r.left + r.width / 2 - tip.offsetWidth / 2}px`;
    tip.style.top  = `${r.top - tip.offsetHeight - 6}px`;
  };

  const hide = () => { tip?.remove(); tip = null; };

  document.addEventListener('mouseenter', (e) => {
    const el = e.target.closest('[data-tip]');
    if (el) show(el, el.dataset.tip);
  }, true);

  document.addEventListener('mouseleave', (e) => {
    if (e.target.closest('[data-tip]')) hide();
  }, true);
})();

/* ── Initialise ─────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  Cart.init();
});

/* Export for inline use in templates */
window.MarketCart = Cart;