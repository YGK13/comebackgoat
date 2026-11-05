# comebackgoat.com

- `site/public/index.html`: the landing page (the only static files served; see `vercel.json`).
- `api/apply.js`: stores founding-cohort applications in a **private** Vercel Blob store (`applications/*.json`) and writes a backup line to the runtime log.
- `api/applications.js`: owner-only list of applications with `?key=<ADMIN_KEY>`.

One-time setup in the Vercel dashboard (project `comebackgoat`):
1. Storage, Create, Blob, access **Private**, connect to this project (all environments).
2. Settings, Environment Variables: `ADMIN_KEY` = a long random string.
3. Settings, Domains: add `comebackgoat.com` and `www.comebackgoat.com`, then set the DNS records Vercel shows at your registrar.
