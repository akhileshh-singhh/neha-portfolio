"""Copy the built-in default content (see cms/defaults.py) into the database.

    python manage.py seed_site            # only if no page exists yet
    python manage.py seed_site --force    # wipe pages/blocks and start over
"""
from django.core.management.base import BaseCommand

from cms.defaults import default_home_spec
from cms.models import Item, Page, Section, SiteSettings, Theme


def seed(force=False):
    """Returns the number of blocks created (0 if nothing was done)."""
    SiteSettings.load()
    Theme.load()
    if Page.objects.exists():
        if not force:
            return 0
        Page.objects.all().delete()
    page = Page.objects.create(title="Home", slug="home", is_home=True)
    specs = default_home_spec()
    for n, spec in enumerate(specs, start=1):
        items = spec.pop("items")
        sec = Section.objects.create(page=page, order=n, **spec)
        for m, it in enumerate(items, start=1):
            Item.objects.create(section=sec, order=m, **it)
    return len(specs)


class Command(BaseCommand):
    help = "Create the starter content (a copy of the current static website)."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="delete existing pages/blocks first")

    def handle(self, *args, **opts):
        n = seed(opts["force"])
        if n:
            self.stdout.write(self.style.SUCCESS(f"Seeded {n} content blocks on the home page."))
        else:
            self.stdout.write("Pages already exist - nothing to do (use --force to start over).")
