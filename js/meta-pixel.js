/* Debtrex Solutions — Meta Pixel (consent-gated)
   - Loads only if user grants 'marketing' consent
   - Generates event_id for CAPI deduplication
   - Exposes window.debtrexFireLead() for the thank-you page
   - PIXEL ID: replace META_PIXEL_ID below before going live
   ============================================================ */

(function () {
  'use strict';

  // === CONFIG =================================================
  const META_PIXEL_ID = 'REPLACE_WITH_META_PIXEL_ID';
  // ============================================================

  let pixelLoaded = false;

  function loadPixel() {
    if (pixelLoaded) return;
    if (!META_PIXEL_ID || META_PIXEL_ID === 'REPLACE_WITH_META_PIXEL_ID') {
      console.warn('[Debtrex] Meta Pixel ID not configured.');
      return;
    }
    pixelLoaded = true;

    // Standard Meta Pixel base
    !function(f,b,e,v,n,t,s){
      if(f.fbq)return;n=f.fbq=function(){n.callMethod ?
        n.callMethod.apply(n,arguments):n.queue.push(arguments)};
      if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
      n.queue=[];t=b.createElement(e);t.async=!0;
      t.src=v;s=b.getElementsByTagName(e)[0];
      s.parentNode.insertBefore(t,s);
    }(window, document, 'script', 'https://connect.facebook.net/en_US/fbevents.js');

    fbq('init', META_PIXEL_ID);
    fbq('track', 'PageView');
  }

  function unloadPixel() {
    // Best-effort: prevent further events (full unload requires reload)
    if (window.fbq) {
      window.fbq = function () { /* disabled by consent */ };
    }
  }

  // === EVENT_ID GENERATOR (for CAPI deduplication) ============
  function makeEventId() {
    const random = Math.random().toString(36).slice(2, 10);
    return `dr_${Date.now()}_${random}`;
  }

  // === FBP / FBC COOKIE READERS (for CAPI matching) ===========
  function readCookie(name) {
    const m = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
    return m ? decodeURIComponent(m[1]) : null;
  }
  window.debtrexGetFbCookies = function () {
    return { fbp: readCookie('_fbp'), fbc: readCookie('_fbc') };
  };

  // === PUBLIC: FIRE LEAD ======================================
  // Returns event_id so the same ID can be sent server-side via CAPI
  window.debtrexFireLead = function (extra) {
    const eventId = makeEventId();
    if (window.fbq && pixelLoaded) {
      window.fbq('track', 'Lead', extra || {}, { eventID: eventId });
    }
    return eventId;
  };

  // === CONSENT GATING =========================================
  function handleConsent(c) {
    if (c && c.marketing === true) loadPixel();
    else unloadPixel();
  }

  // React to current state on load
  if (window.debtrexConsent) handleConsent(window.debtrexConsent);

  // React to changes from the cookie banner
  document.addEventListener('debtrex:consent', function (e) {
    handleConsent(e.detail);
  });
})();
