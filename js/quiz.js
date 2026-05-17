/* Debtrex Solutions — Quiz logic
   - Multi-step navigation with validation
   - Tier calculation (A / B / C / disqualified)
   - Captures UTM params + consent metadata
   - Submits to GoHighLevel webhook (placeholder)
   ============================================================ */

(function () {
  'use strict';

  // === CONFIG =================================================
  // Default: posts to your own /api/lead serverless function, which
  // forwards to GoHighLevel + fires Meta CAPI server-side. This keeps
  // your GHL webhook URL and Meta access token out of the browser.
  // If you don't deploy the serverless function, set this to the GHL
  // webhook URL directly — but you'll lose CAPI dedup.
  const WEBHOOK_URL = '/api/lead';
  const TOTAL_STEPS = 7;
  // ============================================================

  const form = document.getElementById('quizForm');
  const panes = Array.from(document.querySelectorAll('.step-pane'));
  const btnNext = document.getElementById('btnNext');
  const btnBack = document.getElementById('btnBack');
  const progressFill = document.getElementById('progressFill');
  const stepLabel = document.getElementById('stepLabel');
  const stepPct = document.getElementById('stepPct');

  let currentStep = 1;
  const answers = {};

  // === UTM CAPTURE ============================================
  function captureUtms() {
    const params = new URLSearchParams(window.location.search);
    const utm = {};
    ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'fbclid', 'gclid'].forEach(k => {
      const v = params.get(k);
      if (v) utm[k] = v;
    });
    return utm;
  }
  const utms = captureUtms();

  // === RENDER =================================================
  function showStep(n) {
    panes.forEach(p => p.classList.remove('active'));
    const pane = document.querySelector(`.step-pane[data-step="${n}"]`);
    if (pane) pane.classList.add('active');

    const pct = Math.round((n / TOTAL_STEPS) * 100);
    progressFill.style.width = pct + '%';
    stepLabel.textContent = `Step ${n} of ${TOTAL_STEPS}`;
    stepPct.textContent = pct + '%';

    btnBack.style.visibility = n === 1 ? 'hidden' : 'visible';
    btnNext.textContent = n === TOTAL_STEPS ? 'See My Options →' : 'Continue →';

    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  // === VALIDATION =============================================
  function clearErrors(pane) {
    pane.querySelectorAll('.field.error').forEach(f => f.classList.remove('error'));
  }

  function validateStep(n) {
    const pane = document.querySelector(`.step-pane[data-step="${n}"]`);
    clearErrors(pane);

    // Radio groups: data-field on .option-grid
    const radioGroups = pane.querySelectorAll('[data-field]');
    for (const group of radioGroups) {
      const name = group.dataset.field;
      const checked = pane.querySelector(`input[name="${name}"]:checked`);
      if (!checked) {
        group.style.outline = '2px solid #C0392B';
        group.style.outlineOffset = '4px';
        group.style.borderRadius = '8px';
        setTimeout(() => { group.style.outline = ''; }, 1800);
        return false;
      }
      answers[name] = checked.value;
    }

    // Field-based steps (state, contact)
    if (n === 5) {
      const state = pane.querySelector('#state');
      if (!state.value) {
        state.parentElement.classList.add('error');
        return false;
      }
      answers.state = state.value;
    }

    if (n === 7) {
      const name = pane.querySelector('#first_name');
      const phone = pane.querySelector('#phone');
      const email = pane.querySelector('#email');
      const consent = pane.querySelector('#tcpa_consent');
      let ok = true;

      if (!name.value.trim() || name.value.trim().length < 2) {
        name.parentElement.classList.add('error'); ok = false;
      }

      const digits = phone.value.replace(/\D/g, '');
      if (digits.length !== 10) {
        phone.parentElement.classList.add('error'); ok = false;
      }

      const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRe.test(email.value.trim())) {
        email.parentElement.classList.add('error'); ok = false;
      }

      if (!consent.checked) {
        const consentBlock = pane.querySelector('.consent-block');
        consentBlock.style.borderColor = '#C0392B';
        consentBlock.querySelector('.field-error').style.display = 'block';
        ok = false;
      }

      if (!ok) return false;

      answers.full_name = name.value.trim();
      answers.phone = digits;
      answers.phone_formatted = formatPhone(digits);
      answers.email = email.value.trim().toLowerCase();
      answers.tcpa_consent = true;
      answers.consent_text = consent.parentElement.querySelector('span').innerText.trim().replace(/\s+/g, ' ');
      answers.consent_timestamp = new Date().toISOString();
    }

    return true;
  }

  function formatPhone(d) {
    if (d.length !== 10) return d;
    return `(${d.slice(0,3)}) ${d.slice(3,6)}-${d.slice(6)}`;
  }

  // === TIER LOGIC =============================================
  // Per strategy doc:
  //  Tier A: high debt + hardship → 15-20 min SLA
  //  Tier B: medium qualification → 30-45 min SLA
  //  Tier C: low debt / weak profile → 45+ min, nurture
  //  Disqualified: under $10k AND not behind AND employed
  function calculateTier(a) {
    const debtRank = { 'under_10k': 0, '10k_20k': 1, '20k_50k': 2, '50k_plus': 3 };
    const incomeRank = { 'under_2k': 0, '2k_4k': 1, '4k_6k': 2, '6k_plus': 3 };

    const debt = debtRank[a.debt_amount] ?? 0;
    const income = incomeRank[a.income] ?? 0;
    const behind = a.behind_payments === 'yes';
    const occasional = a.behind_payments === 'occasionally';
    const employed = ['full_time', 'part_time', 'self_employed', 'retired'].includes(a.employment);

    // Disqualify: under $10k, not behind, employed
    if (debt === 0 && !behind && !occasional) {
      return { tier: 'D', sla_minutes: null, reason: 'low_debt_no_hardship' };
    }

    // Tier A: $50k+ OR ($20-50k + behind)
    if (debt === 3 || (debt === 2 && behind)) {
      return { tier: 'A', sla_minutes: 20, reason: 'high_debt_hardship' };
    }

    // Tier B: $20k+ OR ($10-20k + behind/occasional)
    if (debt >= 2 || (debt === 1 && (behind || occasional))) {
      return { tier: 'B', sla_minutes: 45, reason: 'medium_qualification' };
    }

    // Otherwise Tier C
    return { tier: 'C', sla_minutes: 90, reason: 'low_qualification' };
  }

  // === SUBMISSION =============================================
  async function submitLead() {
    // Honeypot check
    const honey = form.querySelector('input[name="website"]');
    if (honey && honey.value) {
      // Silent fail — looks successful to the bot
      window.location.href = 'thank-you.html';
      return;
    }

    const tierInfo = calculateTier(answers);

    // Generate event_id NOW so the browser pixel (on the thank-you page)
    // and the server-side CAPI use the same ID — Meta will deduplicate.
    const eventId = 'dr_' + Date.now() + '_' + Math.random().toString(36).slice(2, 10);
    try { sessionStorage.setItem('debtrex_event_id', eventId); } catch (_) {}

    // Capture Meta browser cookies (fbp/fbc) for CAPI matching
    const fbCookies = (typeof window.debtrexGetFbCookies === 'function')
      ? window.debtrexGetFbCookies()
      : { fbp: null, fbc: null };

    const payload = {
      ...answers,
      ...tierInfo,
      utm: utms,
      fbp: fbCookies.fbp,
      fbc: fbCookies.fbc,
      event_id: eventId,
      page_url: window.location.href,
      referrer: document.referrer || null,
      user_agent: navigator.userAgent,
      submitted_at: new Date().toISOString(),
      source: 'debtrex_website_quiz_v1'
    };

    // Lock the button
    btnNext.disabled = true;
    btnNext.textContent = 'Submitting…';
    btnNext.style.opacity = '0.7';

    try {
      const isSameOrigin = WEBHOOK_URL.startsWith('/') || WEBHOOK_URL.includes(window.location.host);
      await fetch(WEBHOOK_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        // Use cors when posting to our own /api/lead so we can read the response;
        // use no-cors if posting directly to a third-party webhook (GHL).
        mode: isSameOrigin ? 'cors' : 'no-cors'
      });
    } catch (err) {
      console.error('[Debtrex] Submission error:', err);
      // Don't block the user — still proceed to thank-you
    }

    // Stash tier in sessionStorage so thank-you page can show appropriate messaging
    try {
      sessionStorage.setItem('debtrex_tier', tierInfo.tier);
      sessionStorage.setItem('debtrex_name', answers.full_name || '');
    } catch (_) {}

    window.location.href = 'thank-you.html';
  }

  // === EVENT WIRING ===========================================
  btnNext.addEventListener('click', function () {
    if (!validateStep(currentStep)) return;

    if (currentStep === TOTAL_STEPS) {
      submitLead();
      return;
    }

    currentStep += 1;
    showStep(currentStep);
  });

  btnBack.addEventListener('click', function () {
    if (currentStep > 1) {
      currentStep -= 1;
      showStep(currentStep);
    }
  });

  // Auto-advance on radio select (steps 1-4, 6)
  panes.forEach(pane => {
    const stepNum = parseInt(pane.dataset.step, 10);
    if ([1, 2, 3, 4, 6].includes(stepNum)) {
      pane.querySelectorAll('input[type="radio"]').forEach(radio => {
        radio.addEventListener('change', function () {
          setTimeout(() => {
            if (currentStep === stepNum && validateStep(stepNum)) {
              if (currentStep < TOTAL_STEPS) {
                currentStep += 1;
                showStep(currentStep);
              }
            }
          }, 180);
        });
      });
    }
  });

  // Phone formatting as user types
  const phoneInput = document.getElementById('phone');
  if (phoneInput) {
    phoneInput.addEventListener('input', function (e) {
      const d = e.target.value.replace(/\D/g, '').slice(0, 10);
      if (d.length === 0) { e.target.value = ''; return; }
      if (d.length < 4) e.target.value = d;
      else if (d.length < 7) e.target.value = `(${d.slice(0,3)}) ${d.slice(3)}`;
      else e.target.value = `(${d.slice(0,3)}) ${d.slice(3,6)}-${d.slice(6)}`;
    });
  }

  // Allow Enter to advance
  form.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA') {
      e.preventDefault();
      btnNext.click();
    }
  });

  // Init
  showStep(1);

})();
