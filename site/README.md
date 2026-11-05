# comebackgoat.com

Static landing page plus two Vercel Functions:
- `api/apply.js` stores founding-cohort applications in a **private** Vercel Blob store (`applications/*.json`).
- `api/applications.js` lists them for the owner when called with `?key=<ADMIN_KEY>`.

Deploy: create a Vercel project with root directory `site`, framework "Other"; connect a private Blob store to the project (Storage, Create, Blob, access Private); add an `ADMIN_KEY` environment variable (a long random string); add the domains comebackgoat.com and www.comebackgoat.com.
