# Neha Varma portfolio – Django backend + admin dashboard

The website you had as one static `index.html` is now rendered by Django from the database,
so **every word, photo, colour, font and the order of every section can be changed from `/admin/`** – no code needed.

## Run it locally (2 minutes)

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                   # DEBUG=1 for local work
python manage.py migrate
python manage.py seed_site                             # loads today's website content into the database
python manage.py createsuperuser                       # your admin login
python manage.py runserver
```
* Website: http://127.0.0.1:8000/  ·  Admin: http://127.0.0.1:8000/admin/

## Works even without a database
The values from your original `index.html` are built in (`cms/defaults.py`). If the database is empty, missing or unreachable,
the site still renders the full page with those defaults. In the admin, an **“Import default content”** button on the dashboard
copies them into the database once so you can start editing (same as `python manage.py seed_site`).

Static files (CSS) are served automatically, so the site and admin look right even without `collectstatic` or `DEBUG=1`.

## How the admin explains itself
* **Page map** – your whole website top to bottom as cards with a live thumbnail of each block and an **Edit** button.
* **Block editor** – pick a block type and the form shows *only the fields that type uses*, renamed to what they look like on the
  website (“Giant word”, “Small italic line”…), each with a one-line note about where it appears. A live preview of the block sits beside the form;
  colours / padding / alignment you change in its Design box update the preview instantly.
* **Theme & design** – every colour says which blocks use it, and the site preview beside the form updates while you type (nothing is saved until you press Save).
* **Site settings** – each field says where it shows up (info row, hire bar, Google results…).
* Custom login page, calm light theme, sticky Save bar, drag-to-reorder, hide/show, duplicate.

## What you can manage in the admin

| Admin section | What it controls |
|---|---|
| **Page sections** | Every section of the page, top to bottom. **Drag to re-order**, tick *Visible* to hide, *Duplicate* via the action menu, add new ones. 21 block types that match your current design (title banner, info row, services list, case study, photo grid, stats, tiles, video, contact form, custom HTML, …). A guide under the *Kind* dropdown tells you which field does what. |
| **Items** (inside a block) | The repeating bits: list rows, photos, tiles, chips, stats, case-study rows. Drag to re-order. |
| **Theme & design** | All colours (colour pickers), font + Google-Fonts link, text size, line height, content width, scrolling-strip speed, plus a free **Custom CSS** box. |
| **Per-block Design box** | Background colour / gradient / image, text colour, alignment, padding, min-height, font, extra CSS classes and custom CSS for that block only. |
| **Site settings** | Your name, email, phone, LinkedIn, handle, SEO title/description, favicon, share image, the floating *Hire* bar, tracking code. |
| **Pages** | Add more pages (e.g. `/about/`), SEO per page, draft/published. Staff can preview drafts at `/preview/<slug>/`. |
| **Media library** | Upload files once, copy the link for custom CSS/HTML. |
| **Inbox** | Messages from the *Contact form* block (spam-protected: honeypot + rate limit). |

### Text tricks (work in every heading / paragraph field)
`*word*` → *italic* · `**word**` → **bold** · press Enter → line break. HTML is escaped, so nothing can break the page.

### Empty photo boxes
Boxes that say “Add photo” turn into real images as soon as you upload one in the block's items (or the block's *Image* field).

## JSON API (for a future Next.js / mobile front-end)
* `GET /api/site/` – settings + theme (+ ready-made CSS variables)
* `GET /api/pages/` and `GET /api/pages/<slug>/` (`home` works as an alias) – page with ordered blocks + items
* `POST /api/contact/` – `{name, email, message}` (5 per hour per IP)

## Deploy
**Render** – push to GitHub → *New → Blueprint* → pick the repo (`render.yaml` is included). Set `DJANGO_SUPERUSER_PASSWORD` in the dashboard; the build creates the login and loads the starter content.
Uploads must live somewhere permanent: the blueprint mounts a Render disk at `/var/data` (paid plan). On a free plan use S3/Cloudinary storage instead.
Any other host: `./build.sh` then `gunicorn config.wsgi`. Set `SECRET_KEY`, `DEBUG=0`, `ALLOWED_HOSTS`, `DATABASE_URL`, `CSRF_TRUSTED_ORIGINS`.

Point your domain (or the Netlify site name) to the Django host when you are happy; the old static site can then be retired.

## Project map
```
config/            settings, urls
cms/models.py      SiteSettings, Theme, Page, Section(+Item), Asset, Inquiry
cms/admin.py       the dashboard
cms/admin_ui.py    plain-language names / hints for every block type (edit this to rename things in the admin)
cms/templates/cms  page layout + one template per block kind (cms/sections/*.html)
cms/static/cms/site.css   your original CSS, driven by theme variables
cms/defaults.py    the built-in default content (your original page)
cms/management/    seed_site, ensure_admin
python manage.py test cms   → 13 tests
```
To add a brand-new block type: add it to `KIND_CHOICES` / `KIND_GUIDES` in `cms/models.py`, create `cms/templates/cms/sections/<kind>.html`, `makemigrations`.
