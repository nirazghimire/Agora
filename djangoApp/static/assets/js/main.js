/**
 * MARKETPLACE — main.js
 * Handles: navbar scroll, mobile drawer, product search, cart badge,
 * alert dismiss, and add-to-cart feedback.
 */

"use strict";

const $ = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];
// these are helper functions for selecting the html elements ; instead of typing document.querySelector.... every time, these helper functions would reduce the entire typeing to few words;


function initNavbarScroll() {
  const navbar = $(".navbar");
  if (!navbar) return;

  const toggle = () => navbar.classList.toggle("scrolled", window.scrollY > 10);
  // the toggle function 'scrolled to navbarclasslist once the user scrolls more than 10 in terms of Y-axis in the browser' ; the classList.toggle flips the state ; if the class is present, it removes it and if the classname is not present, it adds to it ; 
  window.addEventListener("scroll", toggle, { passive: true });
  toggle();
}

function initMobileNav() {
  const hamburger = $(".navbar__hamburger");
  const drawer = $(".navbar__drawer");
  if (!hamburger || !drawer) return;
  //if no elements found, exit out of the function ; 

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
  const searchInput = document.getElementById("product-search");
  if (!searchInput) return;

  let debounceTimer;
  let latestRequestId = 0;

  searchInput.addEventListener("input", () => {
    clearTimeout(debounceTimer);
    //important concept of debouncing
    // debouncing is a programming/engineering technique that ensures a function or event is only executed once after a specified period of inactivity,effectively limiting the rate at which it triggers ; 
    debounceTimer = setTimeout(() => {
      const searchTerm = searchInput.value.toLowerCase().trim();
      const grid = document.querySelector(".listing-grid");
      let emptyStateContainer = document.querySelector(".listing-empty-state-wrapper");
      const requestId = ++latestRequestId;

      if (emptyStateContainer) emptyStateContainer.style.display = "none";

      fetch(`/search-ajax/?q=${encodeURIComponent(searchTerm)}`)
        .then((res) => {
          if (!res.ok) throw new Error("Search failed");
          return res.text();
        })
        .then((html) => {
          // Ignore stale responses when users type quickly.
          if (requestId !== latestRequestId) return;

          const hasProducts = html.includes('class="listing-card"');
          
          if (!hasProducts) {
            if (grid) {
              grid.innerHTML = "";
              grid.style.display = "none";
            }
            // Ensure empty state wrapper exists
            if (!emptyStateContainer) {
              emptyStateContainer = document.createElement("div");
              emptyStateContainer.className = "listing-empty-state-wrapper";
              emptyStateContainer.innerHTML = '<div class="listing-empty-state"><svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#ccc" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="listing-empty-state__icon"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg><p class="listing-empty-state__text">No product found.</p></div>';
              if (grid) grid.parentNode.insertBefore(emptyStateContainer, grid.nextSibling);
            }
            emptyStateContainer.style.display = "block";
          } else {
            if (grid) {
              grid.innerHTML = html;
              grid.style.display = "grid";
            }
            if (emptyStateContainer) emptyStateContainer.style.display = "none";
          }
        })
        .catch(() => {
          if (requestId !== latestRequestId) return;
          if (grid) {
             grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 3rem; color: #c0392b;">An error occurred while searching.</div>';
          }
        });
    }, 300);
  });
}

function initQuickviewModal() {
  document.addEventListener("click", (e) => {
    const clickedInteractive = e.target.closest(
      "form, button, [data-add-to-cart], .listing-card__add-btn, .nav-btn",
    );
    if (clickedInteractive) return;

    const trigger = e.target.closest(".js-open-quickview");
    const card = e.target.closest(".listing-card[data-product-id]");
    if (!trigger && !card) return;

    // Preserve browser affordances for opening links in a new tab/window.
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;

    const productId = trigger?.dataset.productId || card?.dataset.productId;
    if (!productId) return;

    e.preventDefault();
    openQuickview(productId);
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeQuickview();
  });
}

const Cart = {
  badge: null,
  count: 0,

  init() {
    this.badge = $("#main-cart-badge");
    this.bootstrapCount();
    this.renderCount();
  },

  getServerCount() {
    const raw = document.body?.dataset.cartCount;
    const parsed = Number.parseInt(raw || "", 10);
    return Number.isNaN(parsed) ? null : Math.max(parsed, 0);
  },

  bootstrapCount() {
    const serverCount = this.getServerCount();
    this.count = serverCount === null ? this.getStoredCount() : serverCount;
    this.persistCount();
  },

  getStoredCount() {
    try {
      const parsed = Number.parseInt(
        sessionStorage.getItem("cart_count") || "",
        10,
      );
      return Number.isNaN(parsed) ? 0 : Math.max(parsed, 0);
    } catch {
      return 0;
    }
  },

  persistCount() {
    try {
      sessionStorage.setItem("cart_count", String(this.count));
    } catch {
      // Ignore storage errors (private mode / disabled storage)
    }
  },

  getCount() {
    return this.count;
  },

  setCount(n) {
    const parsed = Number.parseInt(String(n), 10);
    this.count = Number.isNaN(parsed) ? 0 : Math.max(parsed, 0);
    this.persistCount();
    this.renderCount();
  },

  renderCount() {
    if (!this.badge) return;
    const n = this.count;
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

//the JS object here is similar to how a class is written ; it has its own attributes and behavior but is written in the dictionary form and not like a typical class form !

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

    const isAuthenticated = document.body?.dataset.userAuthenticated === "true";

    // Let the form submit normally for logged-out users so backend can
    // redirect to login and show the message.
    if (!isAuthenticated) return;

    e.preventDefault();

    const form = btn.closest("form");
    let shouldBumpCart = false;

    if (form) {
      try {
        const previousCount = Cart.getCount();
        const response = await fetch(form.action, {
          method: "POST",
          body: new FormData(form),
          headers: {
            "X-Requested-With": "XMLHttpRequest",
          },
        });

        if (response.status === 401) {
          const errorData = await response.json().catch(() => null);
          if (errorData?.redirect_url) {
            window.location.href = errorData.redirect_url;
          }
          return;
        }

        if (!response.ok) {
          return;
        }

        const data = await response.json().catch(() => null);
        if (typeof data?.cart_count === "number") {
          Cart.setCount(data.cart_count);
          if (data.cart_count > previousCount && Cart.badge) {
            Cart.badge.classList.remove("pop");
            void Cart.badge.offsetWidth;
            Cart.badge.classList.add("pop");
          }
        } else {
          shouldBumpCart = true;
        }
      } catch (err) {
        console.error("Cart Request Failed:", err);
        return;
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

    if (shouldBumpCart) {
      Cart.bump();
    }
  });
}

//once all of the DOM content is loaded, it fires up all the functions ; the entire js file here acts as a single script which is attached to the base html file ; 
document.addEventListener("DOMContentLoaded", () => {
  initNavbarScroll();
  initMobileNav();
  initProductSearch();
  initQuickviewModal();
  initAlerts();
  initAddToCart();
  Cart.init();

  const isAuthenticated = document.body?.dataset.userAuthenticated === "true";
  if (!isAuthenticated) {
    Cart.setCount(0);
  }

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

function openQuickview(productId) {
  const modal = document.getElementById("quickview-modal");
  const content = document.getElementById("quickview-content");
  if (!modal || !content) return;
  
  modal.classList.add("open");
  modal.setAttribute("aria-hidden", "false");
  content.innerHTML = '';
  document.body.style.overflow = "hidden";
  
  fetch(`/product/${productId}/quickview/`)
    .then(res => {
      if (!res.ok) { throw new Error('Failed to load product'); }
      return res.text();
    })
    .then(html => {
      content.innerHTML = html;
    })
    .catch(err => {
      content.innerHTML = `<div style="text-align: center; padding: 2rem; color: #c0392b;">Could not load product details.</div>`;
    });
}

function closeQuickview() {
  const modal = document.getElementById("quickview-modal");
  if (!modal) return;
  modal.classList.remove("open");
  modal.setAttribute("aria-hidden", "true");
  document.body.style.overflow = "";
}

window.openQuickview = openQuickview;
window.closeQuickview = closeQuickview;
