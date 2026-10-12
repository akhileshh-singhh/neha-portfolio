from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase, override_settings

from .models import Inquiry, Page, Section, Theme, css_safe


@override_settings(ALLOWED_HOSTS=["testserver"])
class SiteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_site", verbosity=0)

    def test_home_renders_all_blocks(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "What I bring to the table.")
        self.assertContains(r, "114% admission growth")

    def test_hidden_block_not_rendered(self):
        Section.objects.filter(kind="brand").update(visible=False)
        self.assertNotContains(self.client.get("/"), "helps brands grow online")

    def test_theme_changes_css_variables(self):
        t = Theme.load(); t.color_red = "#123456"; t.save()
        self.assertContains(self.client.get("/"), "--red:#123456")

    def test_css_values_are_sanitised(self):
        self.assertEqual(css_safe("red;}</style><script>"), "red/stylescript")

    def test_html_in_text_is_escaped(self):
        Section.objects.filter(kind="title").update(heading="<script>x</script> *hi*")
        html = self.client.get("/").content.decode()
        self.assertNotIn("<script>x</script>", html)
        self.assertIn("<i>hi</i>", html)

    def test_only_one_home_page(self):
        Page.objects.create(title="Other", slug="other", is_home=True)
        self.assertEqual(Page.objects.filter(is_home=True).count(), 1)

    def test_draft_page_is_404_but_staff_preview_works(self):
        Page.objects.create(title="Draft", slug="draft", is_published=False)
        self.assertEqual(self.client.get("/draft/").status_code, 404)
        get_user_model().objects.create_superuser("a", "a@a.com", "pw12345678")
        self.client.login(username="a", password="pw12345678")
        self.assertEqual(self.client.get("/preview/draft/").status_code, 200)

    def test_contact_api_and_honeypot(self):
        r = self.client.post("/api/contact/", {"name": "A", "email": "a@a.com", "message": "hi"})
        self.assertEqual(r.status_code, 201)
        self.assertEqual(Inquiry.objects.count(), 1)
        self.client.post("/api/contact/", {"name": "B", "email": "b@b.com", "message": "x", "website": "spam"})
        self.assertEqual(Inquiry.objects.count(), 1)

    def test_api_page(self):
        data = self.client.get("/api/pages/home/").json()
        self.assertEqual(data["slug"], "home")
        self.assertGreater(len(data["sections"]), 10)

    def test_admin_pages_load(self):
        get_user_model().objects.create_superuser("a", "a@a.com", "pw12345678")
        self.client.login(username="a", password="pw12345678")
        for url in ["/admin/", "/admin/cms/section/", "/admin/cms/section/1/change/", "/admin/cms/theme/1/change/",
                    "/admin/cms/sitesettings/1/change/", "/admin/cms/page/1/change/", "/admin/cms/section/map/",
                    "/admin/cms/section/add/", "/block-preview/1/"]:
            self.assertEqual(self.client.get(url).status_code, 200, url)


@override_settings(ALLOWED_HOSTS=["testserver"])
class FallbackTests(TestCase):
    """The site must render its built-in default content with an empty or missing database."""

    def test_defaults_shown_when_no_page_in_db(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "What I bring to the table.")
        self.assertContains(r, "114% admission growth")
        self.assertContains(r, "nehaavarmaa12@gmail.com")
        self.assertEqual(Page.objects.count(), 0)  # nothing was written

    def test_defaults_shown_when_database_is_unavailable(self):
        from unittest import mock

        from django.db import OperationalError

        boom = OperationalError("no such table")
        with mock.patch("cms.views.Page.objects") as pages, \
             mock.patch("cms.models.SiteSettings.load", side_effect=boom), \
             mock.patch("cms.models.Theme.load", side_effect=boom):
            pages.filter.side_effect = boom
            r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Social Media. Strategy. Creative")
        self.assertContains(r, "--red:#7a0f1a")  # default theme

    def test_admin_import_button_copies_defaults(self):
        get_user_model().objects.create_superuser("a", "a@a.com", "pw12345678")
        self.client.login(username="a", password="pw12345678")
        self.assertContains(self.client.get("/admin/"), "built-in default content")
        self.client.post("/admin/import-defaults/")
        self.assertEqual(Section.objects.count(), 22)
        self.assertNotContains(self.client.get("/admin/"), "built-in default content")


@override_settings(ALLOWED_HOSTS=["testserver"])
class AdminUITests(TestCase):
    def test_login_page_is_custom(self):
        r = self.client.get("/admin/login/")
        self.assertContains(r, "Welcome back")

    def test_every_block_kind_has_plain_language_config(self):
        from .admin_ui import KIND_UI
        from .models import KIND_CHOICES
        self.assertEqual({k for k, _ in KIND_CHOICES}, set(KIND_UI))
        for kind, cfg in KIND_UI.items():
            self.assertTrue(cfg["where"], kind)

    def test_block_preview_is_staff_only(self):
        call_command("seed_site", verbosity=0)
        self.assertEqual(self.client.get("/block-preview/1/").status_code, 302)
