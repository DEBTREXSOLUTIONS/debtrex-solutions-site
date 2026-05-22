/* Debtrex Solutions — Partner application form
   - Validates the partner/affiliate application
   - POSTs to /api/partner, which emails the lead to your inbox
   ============================================================ */
(function () {
  'use strict';

  const ENDPOINT = '/api/partner';

  const form = document.getElementById('partnerForm');
  if (!form) return;

  const statusEl = document.getElementById('pf-status');
  const submitBtn = document.getElementById('pf-submit');
  const formWrap = document.getElementById('pf-form-wrap');
  const successEl = document.getElementById('pf-success');
  const consentBlock = form.querySelector('.consent-block');

  function field(name) {
    return form.elements[name];
  }

  function setFieldError(el, hasError) {
    const wrap = el.closest('.field');
    if (wrap) wrap.classList.toggle('error', hasError);
  }

  function validEmail(v) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);
  }

  function showSuccess() {
    if (formWrap) formWrap.style.display = 'none';
    if (successEl) {
      successEl.style.display = 'block';
      successEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }

  // Phone formatting as the user types
  const phoneEl = document.getElementById('pf-phone');
  if (phoneEl) {
    phoneEl.addEventListener('input', function (e) {
      const d = e.target.value.replace(/\D/g, '').slice(0, 10);
      if (!d) { e.target.value = ''; return; }
      if (d.length < 4) e.target.value = d;
      else if (d.length < 7) e.target.value = `(${d.slice(0, 3)}) ${d.slice(3)}`;
      else e.target.value = `(${d.slice(0, 3)}) ${d.slice(3, 6)}-${d.slice(6)}`;
    });
  }

  form.addEventListener('submit', async function (e) {
    e.preventDefault();

    statusEl.textContent = '';
    statusEl.className = 'form-status';

    const name = field('name');
    const email = field('email');
    const track = field('partner_track');
    const consent = field('consent');

    let ok = true;

    const nameOk = name.value.trim().length >= 2;
    setFieldError(name, !nameOk);
    if (!nameOk) ok = false;

    const emailOk = validEmail(email.value.trim());
    setFieldError(email, !emailOk);
    if (!emailOk) ok = false;

    const trackOk = !!track.value;
    setFieldError(track, !trackOk);
    if (!trackOk) ok = false;

    if (consentBlock) consentBlock.classList.toggle('consent-error', !consent.checked);
    if (!consent.checked) ok = false;

    if (!ok) {
      statusEl.textContent = 'Please complete the highlighted fields.';
      statusEl.classList.add('error');
      return;
    }

    // Honeypot — bots fill this hidden field; pretend success and stop.
    const honey = field('website');
    if (honey && honey.value) {
      showSuccess();
      return;
    }

    const payload = {
      name: name.value.trim(),
      company: field('company').value.trim(),
      email: email.value.trim(),
      phone: field('phone').value.trim(),
      partner_track: track.value,
      company_website: field('company_website').value.trim(),
      states: field('states').value.trim(),
      volume: field('volume').value.trim(),
      message: field('message').value.trim(),
      consent: consent.checked,
      website: '',
      page_url: window.location.href,
      submitted_at: new Date().toISOString()
    };

    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = 'Submitting…';
    submitBtn.style.opacity = '0.7';

    try {
      const r = await fetch(ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!r.ok) throw new Error('Request failed: ' + r.status);
      showSuccess();
    } catch (err) {
      console.error('[Debtrex partner] Submission error:', err);
      submitBtn.disabled = false;
      submitBtn.textContent = originalText;
      submitBtn.style.opacity = '1';
      statusEl.innerHTML = 'Sorry — something went wrong sending your application. '
        + 'Please email us directly at <a href="mailto:info@debtrexsolutions.com">info@debtrexsolutions.com</a>.';
      statusEl.classList.add('error');
    }
  });
})();
