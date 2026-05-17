/* Debtrex Solutions — US Cookie Consent (CCPA/CPRA + state privacy laws)
   - Notice-based (not GDPR opt-in)
   - Honors Global Privacy Control (GPC) signal automatically
   - Categories: Essential (always on), Analytics, Marketing
   - Persists in localStorage, fires events for downstream scripts
   - Exposes window.debtrexConsent for Pixel/CAPI gating
   ============================================================ */

(function () {
  'use strict';

  const STORAGE_KEY = 'debtrex_consent_v1';
  const POLICY_VERSION = '2026-01-01';

  // Default state — essentials always on; marketing/analytics opt-out by default
  // (CCPA permits notice-based but several states require opt-out availability)
  const defaultConsent = {
    essential: true,
    analytics: false,
    marketing: false,
    version: POLICY_VERSION,
    timestamp: null,
    method: null // 'accept_all' | 'reject_non_essential' | 'custom' | 'gpc'
  };

  // === GPC SIGNAL HONORING (required by CCPA for sale/share opt-out) ===
  function hasGpcSignal() {
    return typeof navigator !== 'undefined' && navigator.globalPrivacyControl === true;
  }

  function loadConsent() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return null;
      const parsed = JSON.parse(raw);
      if (parsed.version !== POLICY_VERSION) return null;
      return parsed;
    } catch (_) { return null; }
  }

  function saveConsent(c) {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(c)); } catch (_) {}
    window.debtrexConsent = c;
    document.dispatchEvent(new CustomEvent('debtrex:consent', { detail: c }));
  }

  // === DECIDE INITIAL STATE ===
  let consent = loadConsent();

  if (!consent) {
    consent = { ...defaultConsent };
    if (hasGpcSignal()) {
      // GPC signal = automatic opt-out of "sale/share" (i.e., marketing tracking)
      consent.marketing = false;
      consent.analytics = false;
      consent.method = 'gpc';
      consent.timestamp = new Date().toISOString();
      saveConsent(consent);
    }
  }

  window.debtrexConsent = consent;

  // === BANNER RENDERING ===
  function renderBanner() {
    if (document.getElementById('cookieBanner')) return;

    const banner = document.createElement('div');
    banner.className = 'cookie-banner';
    banner.id = 'cookieBanner';
    banner.setAttribute('role', 'dialog');
    banner.setAttribute('aria-label', 'Cookie consent');
    banner.innerHTML = `
      <div class="cookie-banner-row">
        <div class="cookie-banner-text">
          <strong>We value your privacy.</strong> We use cookies to operate this site,
          measure performance, and (with your permission) personalize advertising.
          You can manage your preferences or opt out of the sale/sharing of personal
          information at any time. See our
          <a href="cookie-policy.html">Cookie Policy</a> and
          <a href="privacy.html">Privacy Policy</a>.
        </div>
        <div class="cookie-banner-btns">
          <button type="button" class="btn btn-secondary" id="ckPrefs">Manage Preferences</button>
          <button type="button" class="btn btn-secondary" id="ckReject">Reject Non-Essential</button>
          <button type="button" class="btn btn-primary" id="ckAccept">Accept All</button>
        </div>
      </div>
    `;
    document.body.appendChild(banner);

    // Modal
    const modal = document.createElement('div');
    modal.className = 'cookie-modal-overlay';
    modal.id = 'cookieModal';
    modal.innerHTML = `
      <div class="cookie-modal" role="dialog" aria-modal="true" aria-labelledby="ckModalTitle">
        <h3 id="ckModalTitle">Cookie Preferences</h3>
        <p>Choose which categories of cookies and similar technologies you allow. Essential cookies cannot be disabled because they are required for the site to function.</p>

        <div class="cookie-category">
          <div class="cookie-category-head">
            <strong>Essential</strong>
            <div class="cookie-toggle disabled" aria-label="Essential cookies (required)"></div>
          </div>
          <p>Required for core site functionality including navigation, security, and form submission. Cannot be disabled.</p>
        </div>

        <div class="cookie-category">
          <div class="cookie-category-head">
            <strong>Analytics</strong>
            <div class="cookie-toggle" data-cat="analytics" role="switch" aria-label="Toggle analytics cookies" tabindex="0"></div>
          </div>
          <p>Help us understand how visitors use our site so we can improve it (e.g., page views, bounce rate). No personally identifiable information is shared.</p>
        </div>

        <div class="cookie-category">
          <div class="cookie-category-head">
            <strong>Marketing & Advertising</strong>
            <div class="cookie-toggle" data-cat="marketing" role="switch" aria-label="Toggle marketing cookies" tabindex="0"></div>
          </div>
          <p>Used to deliver and measure relevant advertising on platforms like Meta (Facebook/Instagram). Disabling will not stop ads, but they may be less relevant. This is the category covered by California's "Do Not Sell or Share My Personal Information" right.</p>
        </div>

        <div class="cookie-modal-footer">
          <button type="button" class="btn btn-secondary" id="ckRejectAll2">Reject Non-Essential</button>
          <button type="button" class="btn btn-primary" id="ckSavePrefs">Save Preferences</button>
        </div>
      </div>
    `;
    document.body.appendChild(modal);

    // Wire events
    document.getElementById('ckAccept').addEventListener('click', () => setAll(true, 'accept_all'));
    document.getElementById('ckReject').addEventListener('click', () => setAll(false, 'reject_non_essential'));
    document.getElementById('ckPrefs').addEventListener('click', openModal);
    document.getElementById('ckSavePrefs').addEventListener('click', saveFromModal);
    document.getElementById('ckRejectAll2').addEventListener('click', () => {
      modal.querySelectorAll('.cookie-toggle[data-cat]').forEach(t => t.classList.remove('on'));
      setAll(false, 'reject_non_essential');
    });

    modal.addEventListener('click', (e) => {
      if (e.target === modal) closeModal();
    });

    modal.querySelectorAll('.cookie-toggle[data-cat]').forEach(toggle => {
      toggle.addEventListener('click', () => toggle.classList.toggle('on'));
      toggle.addEventListener('keydown', (e) => {
        if (e.key === ' ' || e.key === 'Enter') {
          e.preventDefault();
          toggle.classList.toggle('on');
        }
      });
    });

    // Show banner if no decision yet (GPC users already saved a decision)
    if (!consent.timestamp) banner.classList.add('show');
  }

  function openModal() {
    const modal = document.getElementById('cookieModal');
    // Sync toggle state from current consent
    modal.querySelectorAll('.cookie-toggle[data-cat]').forEach(t => {
      const cat = t.dataset.cat;
      if (consent[cat]) t.classList.add('on');
      else t.classList.remove('on');
    });
    modal.classList.add('show');
  }
  function closeModal() {
    document.getElementById('cookieModal').classList.remove('show');
  }

  function setAll(value, method) {
    consent = {
      essential: true,
      analytics: value,
      marketing: value,
      version: POLICY_VERSION,
      timestamp: new Date().toISOString(),
      method
    };
    saveConsent(consent);
    document.getElementById('cookieBanner').classList.remove('show');
    closeModal();
  }

  function saveFromModal() {
    const modal = document.getElementById('cookieModal');
    consent = {
      essential: true,
      analytics: modal.querySelector('.cookie-toggle[data-cat="analytics"]').classList.contains('on'),
      marketing: modal.querySelector('.cookie-toggle[data-cat="marketing"]').classList.contains('on'),
      version: POLICY_VERSION,
      timestamp: new Date().toISOString(),
      method: 'custom'
    };
    saveConsent(consent);
    document.getElementById('cookieBanner').classList.remove('show');
    closeModal();
  }

  // === PUBLIC API ===
  window.openCookiePreferences = openModal;

  // "Do Not Sell or Share" link handler — disables marketing immediately
  window.doNotSellOrShare = function () {
    consent.marketing = false;
    consent.analytics = false;
    consent.timestamp = new Date().toISOString();
    consent.method = 'do_not_sell';
    saveConsent(consent);
    alert('Your preference has been saved. Marketing and analytics cookies have been disabled, and we will not sell or share your personal information for cross-context behavioral advertising.');
  };

  // Render after DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', renderBanner);
  } else {
    renderBanner();
  }
})();
