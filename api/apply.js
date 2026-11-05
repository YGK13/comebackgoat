import { put } from '@vercel/blob';

const MAX = { name: 120, email: 200, linkedin: 300, situation: 80, role: 120, goal: 1200 };
const json = (body, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' } });

export function GET() {
  return json({ error: 'Use POST.' }, 405);
}

export async function POST(request) {
  let data;
  try {
    data = await request.json();
  } catch {
    return json({ error: 'Send the form as JSON.' }, 400);
  }
  if (data.website) return json({ ok: true }); // honeypot: bots fill hidden fields
  const clean = {};
  for (const [k, max] of Object.entries(MAX)) clean[k] = String(data[k] ?? '').trim().slice(0, max);
  if (!clean.name || !clean.email || !clean.situation) return json({ error: 'Add your name, email and where you are.' }, 400);
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(clean.email)) return json({ error: 'That email address looks incomplete.' }, 400);
  if (clean.linkedin && !/^https?:\/\//i.test(clean.linkedin)) clean.linkedin = 'https://' + clean.linkedin;
  if (data.consent !== 'on' && data.consent !== true) return json({ error: 'Tick the consent box to apply.' }, 400);

  const now = new Date();
  const record = { ...clean, consent: true, received_at: now.toISOString(), referrer: request.headers.get('referer') || '' };
  const id = `${now.toISOString().replace(/[:.]/g, '-')}-${crypto.randomUUID().slice(0, 8)}`;
  console.log('APPLICATION ' + JSON.stringify({ id, ...record })); // backup copy in runtime logs
  try {
    await put(`applications/${id}.json`, JSON.stringify(record, null, 2), {
      access: 'private',
      contentType: 'application/json',
      addRandomSuffix: false,
    });
  } catch (err) {
    console.error('apply: blob write failed; application kept in runtime log', err?.message);
  }
  await notify(id, record);
  return json({ ok: true });
}

// Optional: email each application to the coach so the cohort-operator skill
// finds it in Gmail (subject "Comeback GOAT application: <name>"). Turns on only
// when RESEND_API_KEY and NOTIFY_EMAIL are set in Vercel. With Resend's shared
// onboarding sender, NOTIFY_EMAIL must be the email on the Resend account.
async function notify(id, record) {
  const apiKey = process.env.RESEND_API_KEY;
  const to = process.env.NOTIFY_EMAIL;
  if (!apiKey || !to) return;
  const text = [
    `New Comeback GOAT application from ${record.name}.`,
    '',
    `Where they are: ${record.situation}`,
    `Last role: ${record.role || '-'}`,
    `90-day win: ${record.goal || '-'}`,
    `LinkedIn: ${record.linkedin || '-'}`,
    `Email: ${record.email}`,
    '',
    'CBG-APPLICATION ' + JSON.stringify({ id, ...record }),
  ].join('\n');
  try {
    const res = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { Authorization: `Bearer ${apiKey}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        from: process.env.NOTIFY_FROM || 'Comeback GOAT <onboarding@resend.dev>',
        to: [to],
        reply_to: record.email,
        subject: `Comeback GOAT application: ${record.name}`,
        text,
      }),
    });
    if (!res.ok) console.error('apply: notify failed', res.status);
  } catch (err) {
    console.error('apply: notify error', err?.message);
  }
}
