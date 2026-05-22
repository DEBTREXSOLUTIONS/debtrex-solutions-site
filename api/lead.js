/* Debtrex Solutions — Serverless lead receiver
   ============================================================
   PURPOSE
   - Accepts POST from the website quiz
   - Sends lead details to your email via Resend
   - Fires Meta Conversions API "Lead" event with hashed PII
   - Uses the event_id provided by the browser pixel so Meta deduplicates
   - Hides your Meta access token and email keys from the client

   PLATFORM
   This is written for Vercel (Node.js serverless function). It runs on
   Netlify Functions, AWS Lambda + API Gateway, and Cloudflare Workers
   with minor adjustments.

   DEPLOY
   1. Put this file at /api/lead.js in a Vercel project
   2. Set environment variables in Vercel dashboard:
        RESEND_API_KEY           from https://resend.com/api-keys
        LEAD_EMAIL_TO            the email address to receive leads
        LEAD_EMAIL_FROM          sender address (e.g. leads@debtrexsolutions.com)
        META_PIXEL_ID            your Meta Pixel ID
        META_CAPI_ACCESS_TOKEN   from Events Manager > Settings > CAPI
        META_TEST_EVENT_CODE     (optional) for testing in Events Manager
        ALLOWED_ORIGIN           https://yourdomain.com  (or *)
   3. Run `vercel --prod` to deploy

   CLIENT WIRING
   In /js/quiz.js, set:
        const WEBHOOK_URL = 'https://yourdomain.com/api/lead';
   The function returns 200 immediately to keep latency low for the user.
   ============================================================ */

const crypto = require('crypto');

// === HELPERS ================================================
function sha256(value) {
  if (value === undefined || value === null) return undefined;
  const v = String(value).trim().toLowerCase();
  if (!v) return undefined;
  return crypto.createHash('sha256').update(v).digest('hex');
}

function normPhone(p) {
  if (!p) return undefined;
  const digits = String(p).replace(/\D/g, '');
  if (!digits) return undefined;
  // Add country code 1 for US numbers if missing
  return digits.length === 10 ? '1' + digits : digits;
}

function setCors(res, origin) {
  res.setHeader('Access-Control-Allow-Origin', origin || '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
}

// === SEND LEAD VIA EMAIL (RESEND) ===========================
async function sendLeadEmail(lead) {
  const apiKey = process.env.RESEND_API_KEY;
  const to = process.env.LEAD_EMAIL_TO;
  const from = process.env.LEAD_EMAIL_FROM || 'Debtrex Leads <notifications@leads.debtrexsolutions.com>';
  if (!apiKey || !to) return { ok: false, skipped: 'no_email_config' };

  const tierLabels = {
    A: '🟢 Tier A — High Value (20 min SLA)',
    B: '🔵 Tier B — Qualified (45 min SLA)',
    C: '🟡 Tier C — Lower Priority (90 min SLA)',
    D: '🔴 Tier D — Disqualified / Nurture'
  };
  const tierLabel = tierLabels[lead.tier] || lead.tier || 'Unknown';

  const subject = `New Lead: ${lead.full_name || 'Unknown'} — Tier ${lead.tier || '?'} — ${lead.debt_amount || 'N/A'}`;

  const html = `
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; color: #1a1a1a;">
      <div style="background: #0B2545; color: white; padding: 20px 24px; border-radius: 8px 8px 0 0;">
        <h1 style="margin: 0; font-size: 20px;">New Debt Relief Lead</h1>
        <p style="margin: 6px 0 0; opacity: 0.85; font-size: 14px;">${tierLabel}</p>
      </div>
      <div style="border: 1px solid #e0e0e0; border-top: none; padding: 24px; border-radius: 0 0 8px 8px;">

        <h2 style="font-size: 16px; color: #0B2545; border-bottom: 2px solid #13A66B; padding-bottom: 6px;">Contact Info</h2>
        <table style="width: 100%; font-size: 14px; border-collapse: collapse;">
          <tr><td style="padding: 6px 0; color: #666; width: 140px;">Name</td><td style="padding: 6px 0; font-weight: bold;">${lead.full_name || '—'}</td></tr>
          <tr><td style="padding: 6px 0; color: #666;">Email</td><td style="padding: 6px 0;"><a href="mailto:${lead.email}">${lead.email}</a></td></tr>
          <tr><td style="padding: 6px 0; color: #666;">Phone</td><td style="padding: 6px 0;"><a href="tel:${lead.phone}">${lead.phone}</a></td></tr>
          <tr><td style="padding: 6px 0; color: #666;">State</td><td style="padding: 6px 0;">${lead.state || '—'}</td></tr>
        </table>

        <h2 style="font-size: 16px; color: #0B2545; border-bottom: 2px solid #13A66B; padding-bottom: 6px; margin-top: 20px;">Financial Profile</h2>
        <table style="width: 100%; font-size: 14px; border-collapse: collapse;">
          <tr><td style="padding: 6px 0; color: #666; width: 140px;">Debt Amount</td><td style="padding: 6px 0; font-weight: bold;">${lead.debt_amount || '—'}</td></tr>
          <tr><td style="padding: 6px 0; color: #666;">Debt Type</td><td style="padding: 6px 0;">${lead.debt_type || '—'}</td></tr>
          <tr><td style="padding: 6px 0; color: #666;">Behind on Payments</td><td style="padding: 6px 0;">${lead.behind_on_payments || '—'}</td></tr>
          <tr><td style="padding: 6px 0; color: #666;">Employment</td><td style="padding: 6px 0;">${lead.employment || '—'}</td></tr>
          <tr><td style="padding: 6px 0; color: #666;">Monthly Income</td><td style="padding: 6px 0;">${lead.income || '—'}</td></tr>
        </table>

        <h2 style="font-size: 16px; color: #0B2545; border-bottom: 2px solid #13A66B; padding-bottom: 6px; margin-top: 20px;">Lead Details</h2>
        <table style="width: 100%; font-size: 14px; border-collapse: collapse;">
          <tr><td style="padding: 6px 0; color: #666; width: 140px;">Tier</td><td style="padding: 6px 0; font-weight: bold;">${tierLabel}</td></tr>
          <tr><td style="padding: 6px 0; color: #666;">TCPA Consent</td><td style="padding: 6px 0;">${lead.tcpa_consent ? '✅ Yes' : '❌ No'}</td></tr>
          <tr><td style="padding: 6px 0; color: #666;">Consent Text</td><td style="padding: 6px 0; font-size: 12px; color: #888;">${lead.tcpa_language || '—'}</td></tr>
          <tr><td style="padding: 6px 0; color: #666;">Submitted</td><td style="padding: 6px 0;">${lead.server_timestamp || new Date().toISOString()}</td></tr>
          <tr><td style="padding: 6px 0; color: #666;">IP Address</td><td style="padding: 6px 0;">${lead.server_ip || '—'}</td></tr>
        </table>

        ${lead.utm_source || lead.utm_campaign ? `
        <h2 style="font-size: 16px; color: #0B2545; border-bottom: 2px solid #13A66B; padding-bottom: 6px; margin-top: 20px;">Attribution</h2>
        <table style="width: 100%; font-size: 14px; border-collapse: collapse;">
          ${lead.utm_source ? `<tr><td style="padding: 6px 0; color: #666; width: 140px;">Source</td><td style="padding: 6px 0;">${lead.utm_source}</td></tr>` : ''}
          ${lead.utm_medium ? `<tr><td style="padding: 6px 0; color: #666;">Medium</td><td style="padding: 6px 0;">${lead.utm_medium}</td></tr>` : ''}
          ${lead.utm_campaign ? `<tr><td style="padding: 6px 0; color: #666;">Campaign</td><td style="padding: 6px 0;">${lead.utm_campaign}</td></tr>` : ''}
          ${lead.utm_content ? `<tr><td style="padding: 6px 0; color: #666;">Content</td><td style="padding: 6px 0;">${lead.utm_content}</td></tr>` : ''}
          ${lead.fbclid ? `<tr><td style="padding: 6px 0; color: #666;">FB Click ID</td><td style="padding: 6px 0; font-size: 12px;">${lead.fbclid}</td></tr>` : ''}
        </table>
        ` : ''}

      </div>
      <p style="font-size: 11px; color: #999; text-align: center; margin-top: 12px;">Sent by Debtrex Solutions lead system</p>
    </div>
  `;

  try {
    const r = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ from, to, subject, html })
    });
    const data = await r.json();
    return { ok: r.ok, status: r.status, id: data.id };
  } catch (err) {
    return { ok: false, error: err.message };
  }
}

// === FIRE META CONVERSIONS API LEAD EVENT ===================
async function fireMetaCapiLead(lead, req) {
  const pixelId = process.env.META_PIXEL_ID;
  const token = process.env.META_CAPI_ACCESS_TOKEN;
  if (!pixelId || !token) return { ok: false, skipped: 'no_capi_config' };

  // Source IP for matching (Vercel forwards via x-forwarded-for)
  const fwd = req.headers['x-forwarded-for'];
  const clientIp = (fwd ? fwd.split(',')[0] : req.socket?.remoteAddress) || '';
  const userAgent = req.headers['user-agent'] || lead.user_agent || '';

  // Hashed user data (PII must be SHA-256, lowercased, trimmed)
  const userData = {
    em: lead.email ? [sha256(lead.email)] : undefined,
    ph: lead.phone ? [sha256(normPhone(lead.phone))] : undefined,
    fn: lead.full_name ? [sha256(lead.full_name.split(' ')[0])] : undefined,
    ln: lead.full_name ? [sha256(lead.full_name.split(' ').slice(1).join(' '))] : undefined,
    st: lead.state ? [sha256(lead.state)] : undefined,
    country: [sha256('us')],
    client_ip_address: clientIp || undefined,
    client_user_agent: userAgent,
    fbp: lead.fbp || undefined,
    fbc: lead.fbc || undefined
  };

  // Strip undefined for cleanliness
  Object.keys(userData).forEach(k => userData[k] === undefined && delete userData[k]);

  const event = {
    event_name: 'Lead',
    event_time: Math.floor(Date.now() / 1000),
    event_id: lead.event_id || ('dr_' + Date.now()),
    event_source_url: lead.page_url || undefined,
    action_source: 'website',
    user_data: userData,
    custom_data: {
      lead_tier: lead.tier || undefined,
      content_name: 'Debt Relief Assessment',
      content_category: lead.tier ? 'Tier ' + lead.tier : 'Lead',
      currency: 'USD',
      value: 0
    }
  };

  const body = { data: [event] };
  if (process.env.META_TEST_EVENT_CODE) {
    body.test_event_code = process.env.META_TEST_EVENT_CODE;
  }

  try {
    const url = `https://graph.facebook.com/v18.0/${pixelId}/events?access_token=${token}`;
    const r = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    const data = await r.json();
    return { ok: r.ok, status: r.status, response: data };
  } catch (err) {
    return { ok: false, error: err.message };
  }
}

// === SIMPLE IN-MEMORY RATE LIMIT ============================
// (For real protection use Vercel KV / Upstash. This is a basic spam filter.)
const recentSubmissions = new Map();
function isRateLimited(ip) {
  const now = Date.now();
  const last = recentSubmissions.get(ip);
  if (last && now - last < 5000) return true;
  recentSubmissions.set(ip, now);
  // GC
  if (recentSubmissions.size > 500) {
    for (const [k, t] of recentSubmissions) {
      if (now - t > 60000) recentSubmissions.delete(k);
    }
  }
  return false;
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
    return res.end('Too Many Requests');
  }

  // Parse body — works on Vercel which already parses JSON for module.exports handlers
  let lead = req.body;
  if (typeof lead === 'string') {
    try { lead = JSON.parse(lead); } catch (_) { lead = null; }
  }

  if (!lead || typeof lead !== 'object') {
    res.statusCode = 400;
    return res.end(JSON.stringify({ error: 'Invalid payload' }));
  }

  // Basic validation
  if (!lead.email || !lead.phone || !lead.tcpa_consent) {
    res.statusCode = 400;
    return res.end(JSON.stringify({ error: 'Missing required fields' }));
  }

  // Honeypot
  if (lead.website) {
    res.statusCode = 200;
    return res.end(JSON.stringify({ ok: true })); // silent for bots
  }

  // Enrich with server-side metadata
  const enriched = {
    ...lead,
    server_ip: clientIp,
    server_timestamp: new Date().toISOString()
  };

  // Fire both in parallel; don't block on slow upstreams
  const [emailResult, metaResult] = await Promise.all([
    sendLeadEmail(enriched),
    fireMetaCapiLead(enriched, req)
  ]);

  // Log for debugging (visible in Vercel function logs)
  console.log('[Debtrex lead]', {
    tier: enriched.tier,
    email_hash: sha256(enriched.email)?.slice(0, 8),
    email: emailResult.ok,
    meta: metaResult.ok
  });

  res.statusCode = 200;
  res.setHeader('Content-Type', 'application/json');
  return res.end(JSON.stringify({
    ok: true,
    email: emailResult.ok,
    meta: metaResult.ok,
    event_id: enriched.event_id || null
  }));
};
