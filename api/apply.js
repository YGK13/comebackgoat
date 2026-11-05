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
  return json({ ok: true });
}
