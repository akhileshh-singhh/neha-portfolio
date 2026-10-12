from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.cache import cache
from django.db import DatabaseError
from django.db.models import Prefetch
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .context_processors import _safe_load
from .defaults import build_default_page
from .models import Inquiry, Item, Page, Section, SiteSettings


def _sections(page):
    return (
        Section.objects.filter(page=page, visible=True)
        .prefetch_related(Prefetch("items", queryset=Item.objects.filter(visible=True), to_attr="vis_items"))
        .order_by("order")
    )


def _render_page(request, page, preview=False, sections=None):
    return render(
        request,
        "cms/page.html",
        {
            "page": page,
            "sections": _sections(page) if sections is None else sections,
            "preview": preview,
            "sent": request.GET.get("sent") == "1",
        },
    )


def home(request):
    """Home page from the database; falls back to the built-in default content
    when there is no page yet or the database is unavailable."""
    try:
        page = Page.objects.filter(is_home=True, is_published=True).first() or Page.objects.filter(is_published=True).first()
        if page:
            return _render_page(request, page, sections=list(_sections(page)))
    except DatabaseError:
        pass
    page, sections = build_default_page()
    return _render_page(request, page, sections=sections)


def page_detail(request, slug):
    try:
        page = Page.objects.filter(slug=slug, is_published=True).first()
    except DatabaseError:
        page = None
    if not page:
        raise Http404
    if page.is_home:
        return redirect("cms:home")
    return _render_page(request, page, sections=list(_sections(page)))


def preview(request, slug):
    """Staff-only preview of a page, even if it is still a draft."""
    if not request.user.is_staff:
        raise Http404
    page = get_object_or_404(Page, slug=slug)
    return _render_page(request, page, preview=True)


@require_POST
def contact_submit(request):
    back = request.META.get("HTTP_REFERER") or "/"
    back = back.split("?")[0].split("#")[0]
    if request.POST.get("website"):  # honeypot, bots fill it in
        return redirect(back + "?sent=1")
    ip = (request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0] or request.META.get("REMOTE_ADDR", "")).strip()
    key = f"contact:{ip}"
    count = cache.get(key, 0)
    if count >= 5:
        messages.error(request, "Too many messages, please try again later.")
        return redirect(back)
    name = request.POST.get("name", "").strip()[:120]
    email = request.POST.get("email", "").strip()[:254]
    message = request.POST.get("message", "").strip()[:5000]
    if not (name and email and message and "@" in email):
        return redirect(back + "?error=1#contact")
    try:
        Inquiry.objects.create(name=name, email=email, message=message)
    except DatabaseError:
        messages.error(request, "Messages are unavailable right now.")
        return redirect(back + "?error=1#contact")
    cache.set(key, count + 1, 3600)
    return redirect(back + "?sent=1#contact")


def robots_txt(request):
    s = _safe_load(SiteSettings)
    lines = ["User-agent: *"]
    lines.append("Allow: /" if s.allow_search_engines else "Disallow: /")
    lines.append("Disallow: /admin/")
    lines.append(f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}")
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")


def sitemap_xml(request):
    urls = []
    try:
        pages = list(Page.objects.filter(is_published=True))
    except DatabaseError:
        pages = []
    if not pages:
        urls.append(f"<url><loc>{request.build_absolute_uri('/')}</loc></url>")
    for p in pages:
        urls.append(
            f"<url><loc>{request.build_absolute_uri(p.get_absolute_url())}</loc>"
            f"<lastmod>{p.updated_at.date().isoformat()}</lastmod></url>"
        )
    xml = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(urls) + "</urlset>"
    return HttpResponse(xml, content_type="application/xml")


@staff_member_required
@require_POST
def import_defaults(request):
    """Admin button: copy the built-in default content into the database so it can be edited."""
    from .management.commands.seed_site import seed

    n = seed(force=False)
    if n:
        messages.success(request, f"Imported the default content: {n} blocks. You can now edit everything.")
    else:
        messages.info(request, "The database already has pages, so nothing was imported.")
    return redirect("admin:index")


@staff_member_required
def block_preview(request, pk):
    """Staff-only: a single block rendered with the site styles (used by the admin previews and the page map)."""
    sec = get_object_or_404(Section.objects.select_related("page"), pk=pk)
    sec.vis_items = list(sec.items.filter(visible=True))
    return render(request, "cms/page.html", {"page": sec.page, "sections": [sec], "bare": True})
