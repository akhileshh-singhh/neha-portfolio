from django.db import DatabaseError

from .models import SiteSettings, Theme


def _safe_load(model):
    """Settings row from the DB, or an unsaved object with the built-in defaults if the DB is unavailable."""
    try:
        return model.load()
    except DatabaseError:
        return model()


def site_globals(request):
    if request.path.startswith("/admin/"):
        return {}
    return {"site": _safe_load(SiteSettings), "theme": _safe_load(Theme)}
