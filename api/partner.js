/* Debtrex Solutions — Partner & Affiliate application receiver
   ============================================================
   PURPOSE
   - Accepts POST from the partners.html application form
   - Emails the application to your inbox via Resend so you
     receive every partner/affiliate lead

   PLATFORM
   Written for Vercel (Node.js serverless function), same as
   /api/lead.js.

   DEPLOY
   1. This file lives at /api/partner.js in the Vercel project
   2. Set environment variables in the Vercel dashboard
      (the first two are already used by /api/lead.js):
        RESEND_API_KEY     from https://resend.com/api-keys
        LEAD_EMAIL_FROM    sender address on a verified Resend domain
        PARTNER_EMAIL_TO   inbox for partner applications
                           (falls back to LEAD_EMAIL_TO, then info@)
        ALLOWED_ORIGIN     https://debtrexsolutions.com  (or *)
   3. Deploy with `vercel --prod`
   ============================================================ */

// === HELPERS ================================================
function setCors(res, origin) {
  res.setHeader('Access-Control-Allow-Origin', origin || '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
}

// Escape user input before placing it in the email HTML
function esc(value) {
  if (value === undefined || value === null) return '';
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// === SIMPLE IN-MEMORY RATE LIMIT ============================
const recentSubmissions = new Map();
function isRateLimited(ip) {
  const now = Date.now();
  const last = recentSubmissions.get(ip);
  if (last && now - last < 5000) return true;
  recentSubmissions.set(ip, now);
  if (recentSubmissions.size > 500) {
    for (const [k, t] of recentSubmissions) {
      if (now - t > 60000) recentSubmissions.delete(k);
    }
  }
  return false;
}

// === SEND APPLICATION VIA EMAIL (RESEND) ====================
async function sendPartnerEmail(app, meta) {
  const apiKey = process.env.RESEND_API_KEY;
  const to = process.env.PARTNER_EMAIL_TO || process.env.LEAD_EMAIL_TO || 'info@debtrexsolutions.com';
  const from = process.env.LEAD_EMAIL_FROM || 'Debtrex Partners <notifications@leads.debtrexsolutions.com>';
  if (!apiKey) return { ok: false, skipped: 'no_email_config' };

  const subject = `New Partner Application: ${app.name || 'Unknown'} — ${app.partner_track || 'Unspecified'}`;

  const row = (label, value) => value
    ? `<tr><td style="padding:6px 0;color:#666;width:170px;vertical-align:top;">${esc(label)}</td><td style="padding:6px 0;font-weight:bold;">${esc(value)}</td></tr>`
    : '';

  const messageBlock = app.message
    ? `<h2 style="font-size:16px;color:#0B2545;border-bottom:2px solid #13A66B;padding-bottom:6px;margin-top:20px;">Message</h2>
       <p style="font-size:14px;line-height:1.6;white-space:pre-wrap;">${esc(app.message)}</p>`
    : '';

  const html = `
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; color: #1a1a1a;">
      <div style="background: #14276E; color: white; padding: 20px 24px; border-radius: 8px 8px 0 0;">
        <h1 style="margin: 0; font-size: 20px;">New Partner / Affiliate Application</h1>
        <p style="margin: 6px 0 0; opacity: 0.85; font-size: 14px;">${esc(app.partner_track || 'Track not specified')}</p>
      </div>
      <div style="border: 1px solid #e0e0e0; border-top: none; padding: 24px; border-radius: 0 0 8px 8px;">

        <h2 style="font-size:16px;color:#0B2545;border-bottom:2px solid #13A66B;padding-bottom:6px;">Applicant</h2>
        <table style="width:100%;font-size:14px;border-collapse:collapse;">
          ${row('Name', app.name)}
          ${row('Date of Birth', app.dob)}
          ${row('Company / Business', app.company)}
          ${app.email ? `<tr><td style="padding:6px 0;color:#666;width:170px;">Email</td><td style="padding:6px 0;"><a href="mailto:${esc(app.email)}">${esc(app.email)}</a></td></tr>` : ''}
          ${app.phone ? `<tr><td style="padding:6px 0;color:#666;">Phone</td><td style="padding:6px 0;"><a href="tel:${esc(app.phone)}">${esc(app.phone)}</a></td></tr>` : ''}
          ${app.company_website ? `<tr><td style="padding:6px 0;color:#666;">Website</td><td style="padding:6px 0;">${esc(app.company_website)}</td></tr>` : ''}
          ${row('Address', app.address)}
        </table>

        <h2 style="font-size:16px;color:#0B2545;border-bottom:2px solid #13A66B;padding-bottom:6px;margin-top:20px;">Partnership Details</h2>
        <table style="width:100%;font-size:14px;border-collapse:collapse;">
          ${row('Partner Track', app.partner_track)}
          ${row('States / Regions', app.states)}
          ${row('Expected Volume', app.volume)}
          ${row('Agreed to be contacted', app.consent ? 'Yes' : 'No')}
        </table>

        ${messageBlock}

        <h2 style="font-size:16px;color:#0B2545;border-bottom:2px solid #13A66B;padding-bottom:6px;margin-top:20px;">Submission</h2>
        <table style="width:100%;font-size:14px;border-collapse:collapse;">
          ${row('Submitted', meta.timestamp)}
          ${row('IP Address', meta.ip)}
          ${row('Page', app.page_url)}
        </table>

      </div>
      <p style="font-size:11px;color:#999;text-align:center;margin-top:12px;">Sent by Debtrex Solutions partner application system</p>
    </div>
  `;

  const payload = { from, to, subject, html };
  if (app.email && EMAIL_RE.test(String(app.email))) {
    payload.reply_to = app.email;
  }

  try {
    const r = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });
    const data = await r.json();
    return { ok: r.ok, status: r.status, id: data.id, error: data.message };
  } catch (err) {
    return { ok: false, error: err.message };
  }
}

// === MAIN HANDLER ===========================================
module.exports = async (req, res) => {
  const allowedOrigin = process.env.ALLOWED_ORIGIN || '*';
  setCors(res, allowedOrigin);

  if (req.method === 'OPTIONS') {
    res.statusCode = 204;
    return res.end();
  }

  if (req.method !== 'POST') {
    res.statusCode = 405;
    return res.end('Method Not Allowed');
  }

  const fwd = req.headers['x-forwarded-for'];
  const clientIp = (fwd ? fwd.split(',')[0] : req.socket?.remoteAddress) || 'unknown';

  if (isRateLimited(clientIp)) {
    res.statusCode = 429;
    res.setHeader('Content-Type', 'application/json');
    return res.end(JSON.stringify({ error: 'Too many requests' }));
  }

  // Parse body
  let app = req.body;
  if (typeof app === 'string') {
    try { app = JSON.parse(app); } catch (_) { app = null; }
  }

  if (!app || typeof app !== 'object') {
    res.statusCode = 400;
    res.setHeader('Content-Type', 'application/json');
    return res.end(JSON.stringify({ error: 'Invalid payload' }));
  }

  // Honeypot — silently accept so bots think they succeeded
  if (app.website) {
    res.statusCode = 200;
    res.setHeader('Content-Type', 'application/json');
    return res.end(JSON.stringify({ ok: true }));
  }

  // Validation
  if (!app.name || !EMAIL_RE.test(String(app.email || '')) || !app.partner_track) {
    res.statusCode = 400;
    res.setHeader('Content-Type', 'application/json');
    return res.end(JSON.stringify({ error: 'Missing required fields' }));
  }

  const result = await sendPartnerEmail(app, {
    ip: clientIp,
    timestamp: new Date().toISOString()
  });

  console.log('[Debtrex partner]', {
    track: app.partner_track,
    email_ok: result.ok,
    skipped: result.skipped || null,
    resend_status: result.status || null,
    resend_error: result.error || null
  });

  // Email config missing — accept the request so the form still works,
  // but the deployment needs RESEND_API_KEY set to actually receive leads.
  if (result.skipped) {
    res.statusCode = 200;
    res.setHeader('Content-Type', 'application/json');
    return res.end(JSON.stringify({ ok: true, email: false, note: result.skipped }));
  }

  // Email genuinely failed to send — tell the client so it can show a fallback.
  if (!result.ok) {
    res.statusCode = 502;
    res.setHeader('Content-Type', 'application/json');
    return res.end(JSON.stringify({ ok: false, error: 'Email delivery failed' }));
  }

  res.statusCode = 200;
  res.setHeader('Content-Type', 'application/json');
  return res.end(JSON.stringify({ ok: true, email: true }));
};
