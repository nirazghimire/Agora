/**
 * MARKETPLACE — main.js
 * Handles: navbar scroll, mobile drawer, product search, cart badge,
 * alert dismiss, and add-to-cart feedback.
 */

"use strict";

const $ = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

function initNavbarScroll() {
  const navbar = $(".navbar");
  if (!navbar) return;

  const toggle = () => navbar.classList.toggle("scrolled", window.scrollY > 10);
  window.addEventListener("scroll", toggle, { passive: true });
  toggle();
}

function initMobileNav() {
  const hamburger = $(".navbar__hamburger");
  const drawer = $(".navbar__drawer");
  if (!hamburger || !drawer) return;

  let open = false;

  const closeDrawer = () => {
    open = false;
    hamburger.classList.remove("open");
    drawer.classList.remove("open");
    hamburger.setAttribute("aria-expanded", "false");
    drawer.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
  };

  hamburger.addEventListener("click", () => {
    open = !open;
    hamburger.classList.toggle("open", open);
    drawer.classList.toggle("open", open);
    hamburger.setAttribute("aria-expanded", String(open));
    drawer.setAttribute("aria-hidden", String(!open));
    document.body.style.overflow = open ? "hidden" : "";
  });


  //searching a product


  document.addEventListener("click", (e) => {
    if (open && !hamburger.contains(e.target) && !drawer.contains(e.target))
      closeDrawer();
  });

  drawer.addEventListener("click", (e) => {
    if (e.target.closest('a, button[type="submit"]')) closeDrawer();
  });
}

function initProductSearch() {
  const searchInput = document.getElementById('product-search');
  if (!searchInput) return;

  const prod = document.querySelectorAll('.listing-card');
  let debounceTimer;

  searchInput.addEventListener('input', () => {
    clearTimeout(debounceTimer);
    //important concept of debouncing
    debounceTimer = setTimeout(() => {
      const searchTerm = searchInput.value.toLowerCase().trim();

      prod.forEach(product => {
        const nameEl = product.querySelector('.listing-card__name');
        const descEl = product.querySelector('.listing-card__desc');
        if (!nameEl) return;

        if (searchTerm.length > 0 && searchTerm.length < 3) {
          product.style.display = 'block';
          return;
        }

        if (searchTerm.length === 0) {
          product.style.display = 'block';
          return;
        }

        const productName = nameEl.textContent.toLowerCase();
        const productDesc = descEl ? descEl.textContent.toLowerCase() : '';

        if (productName.includes(searchTerm) || productDesc.includes(searchTerm)) {
          product.style.display = 'block';
        } else {
          product.style.display = 'none';
        }
      });
    }, 300);
  });
}

const Cart = {
  badge: null,

  init() {
    this.badge = $(".cart-badge");
    this.updateCount();
  },

  getCount() {
    try {
      return parseInt(sessionStorage.getItem("cart_count") || "0", 10);
    } catch {
      return 0;
    }
  },

  setCount(n) {
    try {
      sessionStorage.setItem("cart_count", String(n));
    } catch {
      // Ignore storage errors (private mode / disabled storage)
    }
    this.updateCount();
  },

  updateCount() {
    if (!this.badge) return;
    const n = this.getCount();
    this.badge.textContent = n > 99 ? "99+" : n;
    this.badge.hidden = n === 0;
  },

  bump() {
    this.setCount(this.getCount() + 1);
    if (!this.badge) return;
    this.badge.classList.remove("pop");
    void this.badge.offsetWidth;
    this.badge.classList.add("pop");
  },
};

function initAlerts() {
  document.addEventListener("click", (e) => {
    const btn = e.target.closest(".alert__close");
    if (!btn) return;
    const alert = btn.closest(".alert");
    if (!alert) return;
    alert.classList.add("alert--leaving");
    setTimeout(() => alert.remove(), 220);
  });

  $$(".alert--success").forEach((el) => {
    setTimeout(() => {
      if (!el.isConnected) return;
      el.classList.add("alert--fading");
      setTimeout(() => el.remove(), 520);
    }, 5000);
  });
}

function initAddToCart() {
  document.addEventListener("click", async (e) => {
    const btn = e.target.closest("[data-add-to-cart]");
    if (!btn) return;
    
    e.preventDefault();

    const form = btn.closest("form");
    if (form) {
      try {
        await fetch(form.action, {
          method: "POST",
          body: new FormData(form)
        });
      } catch (err) {
        console.error("Cart Request Failed:", err);
      }
    }

    if (!btn.dataset.defaultLabel) {
      btn.dataset.defaultLabel = btn.innerHTML;
    }

    btn.innerHTML = "Added";
    btn.classList.add("is-adding");
    btn.disabled = true;

    setTimeout(() => {
      btn.innerHTML = btn.dataset.defaultLabel || "Add to Cart";
      btn.classList.remove("is-adding");
      btn.disabled = false;
    }, 1800);

    Cart.bump();
  });
}

document.addEventListener("DOMContentLoaded", () => {
  initNavbarScroll();
  initMobileNav();
  initProductSearch();
  initAlerts();
  initAddToCart();
  Cart.init();
  
  const signoutBtn = document.getElementById("signout-btn");
  const signoutMobileBtn = document.getElementById("signout-btn-mobile");
  
  if (signoutBtn) {
    signoutBtn.addEventListener("click", () => sessionStorage.clear());
  }
  if (signoutMobileBtn) {
    signoutMobileBtn.addEventListener("click", () => sessionStorage.clear());
  }
});

window.MarketCart = Cart;
