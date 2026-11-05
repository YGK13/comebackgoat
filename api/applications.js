import { list, get } from '@vercel/blob';

// Owner-only view of founding-cohort applications. Send the ADMIN_KEY in an
// "x-admin-key" header (preferred: keeps it out of URLs and logs) or as ?key=.
export async function GET(request) {
  const url = new URL(request.url);
  const key = process.env.ADMIN_KEY;
  const given = request.headers.get('x-admin-key') || url.searchParams.get('key');
  if (!key || given !== key) {
    return new Response('Not found', { status: 404 });
  }
  const { blobs } = await list({ prefix: 'applications/', limit: 1000 });
  const rows = [];
  for (const b of blobs) {
    const r = await get(b.pathname, { access: 'private' });
    if (r?.statusCode === 200) rows.push(JSON.parse(await new Response(r.stream).text()));
  }
  rows.sort((a, b) => (a.received_at < b.received_at ? 1 : -1));
  return new Response(JSON.stringify({ count: rows.length, applications: rows }, null, 2), {
    headers: { 'Content-Type': 'application/json', 'Cache-Control': 'private, no-store', 'X-Robots-Tag': 'noindex' },
  });
}
