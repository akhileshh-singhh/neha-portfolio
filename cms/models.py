import re

from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse

# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

_UNSAFE_CSS = re.compile(r"[;{}<>\"'\\]")


def css_safe(value, limit=300):
    """Strip characters that could break out of an inline style attribute."""
    return _UNSAFE_CSS.sub("", str(value or "")).strip()[:limit]


class ColorField(models.CharField):
    """A CSS colour (or any CSS background value) with a colour-picker widget."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 120)
        kwargs.setdefault("blank", True)
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        from .widgets import ColorPickerWidget

        kwargs["widget"] = ColorPickerWidget  # admin passes its own text widget; replace it
        return super().formfield(**kwargs)


class SingletonModel(models.Model):
    """Exactly one row (pk=1).  Used for site-wide settings and the theme."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):  # never delete the singleton
        pass

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


# --------------------------------------------------------------------------
# site-wide settings
# --------------------------------------------------------------------------


class SiteSettings(SingletonModel):
    display_name = models.CharField(
        max_length=120, default="Neha Varma", help_text="Appears: top-left link of the info row (links to LinkedIn) and in the browser tab title of extra pages."
    )
    site_title = models.CharField(
        max_length=160, default="Neha Varma | Creative Portfolio", help_text="Appears: the browser tab text and the blue title in Google results (home page)."
    )
    meta_description = models.CharField(
        max_length=300, blank=True, help_text="Appears: the grey text under your link in Google results and in WhatsApp / LinkedIn link previews."
    )
    favicon = models.ImageField(upload_to="site/", blank=True, help_text="Appears: the tiny icon in the browser tab.")
    share_image = models.ImageField(
        upload_to="site/", blank=True, verbose_name="Social share image",
        help_text="Image shown when the site link is shared on WhatsApp, LinkedIn, etc.",
    )
    allow_search_engines = models.BooleanField(
        default=True, help_text="Untick to ask Google not to index the site (robots.txt + noindex)."
    )

    # contact
    email = models.EmailField(blank=True, default="nehaavarmaa12@gmail.com", help_text="Appears: under the photos in the info row, and as the “Hire” button link (mailto:).")
    phone = models.CharField(max_length=40, blank=True, default="+91 9082988199", help_text="Appears: under the email in the info row, and as the second hire-bar button (tel:).")
    linkedin_url = models.URLField(blank=True, default="https://www.linkedin.com/in/nehavarma", help_text="Appears: the “in  Neha Varma” link at the top-left of the info row.")

    # floating "available for hire" bar
    bar_enabled = models.BooleanField(default=True, verbose_name="Show the floating hire bar")
    bar_avatar_text = models.CharField(max_length=4, default="NV", verbose_name="Avatar letters")
    bar_avatar_bg = ColorField(help_text="Leave empty to use the lime theme colour.")
    bar_message = models.CharField(max_length=160, default="Neha is available for hire")
    bar_primary_label = models.CharField(max_length=40, default="Hire Neha")
    bar_primary_url = models.CharField(
        max_length=300, blank=True, help_text="Leave empty to use mailto: your email."
    )
    bar_secondary_label = models.CharField(max_length=40, blank=True, default="Save Candidate")
    bar_secondary_url = models.CharField(
        max_length=300, blank=True, help_text="Leave empty to use tel: your phone."
    )

    # advanced
    head_html = models.TextField(
        blank=True, verbose_name="Extra <head> HTML", help_text="Analytics, verification tags, etc. Pasted as-is."
    )
    body_end_html = models.TextField(
        blank=True, verbose_name="Extra HTML before </body>", help_text="Chat widgets, tracking pixels, etc. Pasted as-is."
    )

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self):
        return "Site settings"

    @property
    def bar_primary_href(self):
        return self.bar_primary_url or (f"mailto:{self.email}" if self.email else "")

    @property
    def bar_secondary_href(self):
        if self.bar_secondary_url:
            return self.bar_secondary_url
        digits = re.sub(r"[^\d+]", "", self.phone or "")
        return f"tel:{digits}" if digits else ""

    @property
    def phone_href(self):
        digits = re.sub(r"[^\d+]", "", self.phone or "")
        return f"tel:{digits}" if digits else ""


class Theme(SingletonModel):
    """Design tokens.  Every colour on the site is one of these variables."""

    # colours -----------------------------------------------------------
    color_black = ColorField(default="#000000", verbose_name="Page background (black)", help_text="Page background and the black blocks: title banner, services list, brand intro, photo label, videos, closing block.")
    color_black_2 = ColorField(default="#111111", verbose_name="Dark section background", help_text="The slightly lighter dark of the info row (photos + contact), the “What I bring” block and the contact form.")
    color_text = ColorField(default="#f4f4f1", verbose_name="Main text colour", help_text="Default text colour on all dark blocks.")
    color_muted = ColorField(default="#8d8d8a", verbose_name="Muted text / lines", help_text="Small grey text and thin divider lines: service rows, captions, the “Published” line.")
    color_grey = ColorField(default="#d9d9d6", verbose_name="Ticker strip grey", help_text="Background of the scrolling text strip under the services list.")
    color_teal = ColorField(default="#0b4a40", verbose_name="Teal", help_text="The SoundKraft numbers block and the Templates block.")
    color_lime = ColorField(default="#c8ff2e", verbose_name="Lime", help_text="Lime accents: “post.” tile, hire-bar avatar, first closing thumbnail, form button, keyboard focus ring.")
    color_red = ColorField(default="#7a0f1a", verbose_name="Deep red", help_text="The “Taste Mumbai” photo + headline block.")
    color_olive = ColorField(default="#9bb52a", verbose_name="Olive", help_text="The “Sundown Cafe” big statement block.")
    color_gold = ColorField(default="#e5a50a", verbose_name="Gold", help_text="The two-photo block under Sundown Cafe.")
    color_ink = ColorField(default="#000000", verbose_name="Dark text on light colours", help_text="Dark text sitting on light colours: scrolling strip, coloured tiles, round logo, lime buttons.")
    color_paper = ColorField(default="#e4e4e1", verbose_name="Light card background", help_text="Background of the light case-study cards (dance academy, home decor).")
    color_paper_text = ColorField(default="#111111", verbose_name="Light card text", help_text="Text colour on the light case-study cards.")
    color_card_dark = ColorField(default="#161615", verbose_name="Dark card background", help_text="Background of the dark case-study card (fitness brand).")
    color_placeholder_from = ColorField(default="#3a3a37", verbose_name="Empty photo gradient (start)", help_text="Empty “Add photo” boxes: gradient start colour.")
    color_placeholder_to = ColorField(default="#161615", verbose_name="Empty photo gradient (end)", help_text="Empty “Add photo” boxes: gradient end colour.")
    color_bar_bg = ColorField(default="rgba(30,30,30,.92)", verbose_name="Floating bar background", help_text="The floating “available for hire” bar at the bottom of the screen.")
    color_accent = ColorField(default="#1769ff", verbose_name="Accent (thumb badge etc.)", help_text="The round thumbs-up badge in the closing block.")

    # typography & layout ---------------------------------------------------
    font_family = models.CharField(
        max_length=300, default='"Inter Tight","Helvetica Neue",Arial,sans-serif',
        help_text='Affects: every piece of text on the website. A CSS font stack, e.g. "Playfair Display", Georgia, serif',
    )
    google_fonts_url = models.URLField(
        max_length=600, blank=True,
        default="https://fonts.googleapis.com/css2?family=Inter+Tight:ital,wght@0,400;0,500;0,800;1,500;1,800&display=swap",
        help_text="Paste the Google Fonts CSS link for the font above (fonts.google.com > Get embed code). Leave empty to use only system fonts.",
    )
    base_font_size = models.PositiveSmallIntegerField(default=17, help_text="Affects: size of normal paragraph text everywhere (px). Big headings scale separately.")
    line_height = models.DecimalField(max_digits=3, decimal_places=2, default=1.45, help_text="Affects: spacing between lines of paragraph text.")
    container_width = models.PositiveSmallIntegerField(default=1120, help_text="Affects: how wide the whole page can get on big screens (px).")
    ticker_seconds = models.PositiveSmallIntegerField(default=30, help_text="Affects: the scrolling text strip under the services list. Seconds per loop (bigger = slower).")
    animate_ticker = models.BooleanField(default=True)

    custom_css = models.TextField(
        blank=True, verbose_name="Custom CSS (whole site)",
        help_text="Advanced: any CSS here is added last, so it overrides everything.",
    )

    class Meta:
        verbose_name = "Theme & design"
        verbose_name_plural = "Theme & design"

    def __str__(self):
        return "Theme & design"

    COLOR_VARS = {
        "color_black": "--k", "color_black_2": "--k2", "color_text": "--w", "color_muted": "--m",
        "color_grey": "--grey", "color_teal": "--teal", "color_lime": "--lime", "color_red": "--red",
        "color_olive": "--olive", "color_gold": "--gold", "color_ink": "--ink", "color_paper": "--paper",
        "color_paper_text": "--paper-ink", "color_card_dark": "--card-dark",
        "color_placeholder_from": "--ph1", "color_placeholder_to": "--ph2",
        "color_bar_bg": "--bar-bg", "color_accent": "--accent",
    }

    def css_variables(self):
        rows = []
        for field, var in self.COLOR_VARS.items():
            val = css_safe(getattr(self, field))
            if val:
                rows.append(f"{var}:{val}")
        rows.append(f"--font:{css_safe(self.font_family)}")
        rows.append(f"--fs:{int(self.base_font_size)}px")
        rows.append(f"--lh:{self.line_height}")
        rows.append(f"--maxw:{int(self.container_width)}px")
        rows.append(f"--ticker:{int(self.ticker_seconds)}s")
        rows.append("--ticker-play:" + ("running" if self.animate_ticker else "paused"))
        return ":root{" + ";".join(rows) + "}"


# --------------------------------------------------------------------------
# pages & sections
# --------------------------------------------------------------------------


class Page(models.Model):
    title = models.CharField(max_length=160, help_text="Internal name, also the default browser-tab title.")
    slug = models.SlugField(unique=True, help_text="URL: /<slug>/  (the home page lives at /)")
    is_home = models.BooleanField(default=False, help_text="The page shown at the root address /")
    is_published = models.BooleanField(default=True)
    meta_title = models.CharField(max_length=160, blank=True, verbose_name="SEO title")
    meta_description = models.CharField(max_length=300, blank=True, verbose_name="SEO description")
    share_image = models.ImageField(upload_to="pages/", blank=True)
    show_hire_bar = models.BooleanField(default=True, verbose_name="Show floating hire bar on this page")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_home", "title"]

    def __str__(self):
        return self.title + ("  (home)" if self.is_home else "")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_home:  # only one home page
            Page.objects.exclude(pk=self.pk).filter(is_home=True).update(is_home=False)

    def get_absolute_url(self):
        return "/" if self.is_home else reverse("cms:page", args=[self.slug])


KIND_CHOICES = [
    ("title", "Title banner (slashes + big heading)"),
    ("info", "Info row (link, photos, contact, big word)"),
    ("bring", "Three-column strengths + platforms"),
    ("services", "Numbered list rows (+ scrolling strip)"),
    ("rows", "Plain list rows (skills / studies style)"),
    ("fullbleed", "Full-width banner with heading"),
    ("caption", "Caption bar"),
    ("video", "Video block"),
    ("statement", "Big coloured statement"),
    ("photos", "Photo grid / pair / mosaic"),
    ("feature", "Photo + headline split"),
    ("brand", "Brand / agency intro"),
    ("case_study", "Case study (goal / strategy / result)"),
    ("tiles", "Coloured word tiles"),
    ("label", "Small section label"),
    ("stats", "Role + big numbers"),
    ("promo", "Text + mockup image"),
    ("closing", "Closing block with thumbnails"),
    ("contact_form", "Contact form"),
    ("custom_html", "Custom HTML (advanced)"),
    ("spacer", "Empty spacer"),
]

ALIGN_CHOICES = [("", "Default"), ("left", "Left"), ("center", "Centre"), ("right", "Right")]

VIDEO_EXT = FileExtensionValidator(["mp4", "webm", "mov", "m4v"])


class Section(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="sections")
    order = models.PositiveIntegerField(default=0, db_index=True)
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default="statement")
    name = models.CharField(max_length=120, blank=True, help_text="Only for you: how this block is called in the admin list.")
    visible = models.BooleanField(default=True, help_text="Untick to hide this block without deleting it.")
    anchor_id = models.SlugField(blank=True, help_text="Optional link target, e.g. 'work' lets you link to /#work")

    # content
    eyebrow = models.CharField(max_length=300, blank=True)
    heading = models.TextField(blank=True)
    subheading = models.TextField(blank=True)
    body = models.TextField(blank=True)
    footnote = models.TextField(blank=True)

    image = models.ImageField(upload_to="sections/", blank=True)
    image_alt = models.CharField(max_length=200, blank=True)
    placeholder_text = models.CharField(
        max_length=80, blank=True, help_text="Text shown in the grey box while no image is uploaded.",
    )
    video_file = models.FileField(upload_to="videos/", blank=True, validators=[VIDEO_EXT])
    video_url = models.URLField(blank=True, max_length=400, help_text="YouTube, Vimeo or direct .mp4 link.")
    ticker_text = models.CharField(max_length=300, blank=True, help_text="Scrolling strip text (services kind).")
    ticker_speed = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Seconds per loop; empty = theme default.")
    layout = models.CharField(max_length=30, blank=True, help_text="Variant, see the guide above (e.g. pair, mosaic, grid, dark, image-right).")
    columns = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Number of columns (tiles / grid / stats).")

    # design
    bg_color = ColorField(verbose_name="Background colour", help_text="Colour behind this block only. Empty = the normal colour of this block type (set in Theme & design).")
    bg_gradient = models.CharField(
        max_length=300, blank=True, verbose_name="Background gradient",
        help_text="e.g. linear-gradient(90deg,#6b4a2c,#1a1109). Drawn over the background image if both are set.",
    )
    bg_image = models.ImageField(upload_to="backgrounds/", blank=True, verbose_name="Background image")
    text_color = ColorField(verbose_name="Text colour", help_text="Text colour inside this block only.")
    accent_color = ColorField(help_text="Extra colour used by a few block types: the round logo (Brand intro) and the round badge (Closing).")
    align = models.CharField(max_length=10, blank=True, choices=ALIGN_CHOICES, verbose_name="Alignment")
    padding_top = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Space above this block's content, in pixels. Empty = normal.")
    padding_bottom = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Space below this block's content, in pixels. Empty = normal.")
    min_height = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Makes the block at least this tall, in pixels (also the height of a Spacer). Empty = automatic.")
    font_family = models.CharField(max_length=200, blank=True, help_text='Override font for this block, e.g. Georgia, serif')
    css_class = models.CharField(max_length=120, blank=True, help_text="Extra CSS classes.")
    custom_css = models.TextField(
        blank=True, help_text="Advanced. Target this block with  #block-<id>  (the id is in the page URL of this edit screen).",
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Page section"
        verbose_name_plural = "Page sections"

    def __str__(self):
        return self.label

    @property
    def label(self):
        base = self.name or (self.heading or "").replace("\n", " ").replace("*", "")[:50] or self.get_kind_display()
        return base.strip() or f"Block {self.pk}"

    @property
    def dom_id(self):
        return self.anchor_id or f"block-{self.pk}"

    @property
    def template_name(self):
        return f"cms/sections/{self.kind}.html"

    def inline_style(self):
        parts = []
        layers = []
        if self.bg_gradient:
            layers.append(css_safe(self.bg_gradient))
        if self.bg_image:
            layers.append(f"url({self.bg_image.url})")
        if layers:
            parts.append("background-image:" + ",".join(layers))
            parts.append("background-size:cover")
            parts.append("background-position:center")
        if self.bg_color:
            parts.append(f"background-color:{css_safe(self.bg_color)}")
        if self.text_color:
            parts.append(f"color:{css_safe(self.text_color)}")
        if self.accent_color:
            parts.append(f"--sec-accent:{css_safe(self.accent_color)}")
        if self.align:
            parts.append(f"text-align:{self.align}")
            if self.kind == "fullbleed":
                parts.append("justify-content:" + {"left": "flex-start", "center": "center", "right": "flex-end"}[self.align])
        if self.padding_top is not None:
            parts.append(f"padding-top:{int(self.padding_top)}px")
        if self.padding_bottom is not None:
            parts.append(f"padding-bottom:{int(self.padding_bottom)}px")
        if self.min_height is not None:
            parts.append(f"min-height:{int(self.min_height)}px")
        if self.font_family:
            parts.append(f"font-family:{css_safe(self.font_family, 200)}")
        if self.columns and self.kind in {"tiles", "stats"}:
            parts.append(f"--cols:{int(self.columns)}")
        return ";".join(parts)

    def safe_custom_css(self):
        return (self.custom_css or "").replace("</", "<\\/")


class Item(models.Model):
    """A repeatable entry inside a block: a row, a photo, a tile, a stat, a chip..."""

    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="items")
    order = models.PositiveIntegerField(default=0, db_index=True)
    visible = models.BooleanField(default=True)
    SLOT_CHOICES = [
        ("", "Normal item"),
        ("photo", "Photo"),
        ("left", "Left column"),
        ("right", "Right column"),
        ("chip", "Platform pill"),
        ("row", "Goal / Strategy / Result row"),
    ]
    slot = models.CharField(
        max_length=30, blank=True, choices=SLOT_CHOICES, verbose_name="Where it goes",
        help_text="Only matters for blocks that have several groups (the page fills this in for you).",
    )
    title = models.TextField(blank=True)
    text = models.TextField(blank=True)
    image = models.ImageField(upload_to="items/", blank=True)
    url = models.CharField(max_length=400, blank=True, help_text="Optional link.")
    bg_color = ColorField(verbose_name="Background colour")
    text_color = ColorField()

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return (self.title or self.text or f"Item {self.pk}")[:60]

    def inline_style(self):
        parts = []
        if self.bg_color:
            parts.append(f"background:{css_safe(self.bg_color)}")
        if self.text_color:
            parts.append(f"color:{css_safe(self.text_color)}")
        return ";".join(parts)


# --------------------------------------------------------------------------
# media library & inbox
# --------------------------------------------------------------------------


class Asset(models.Model):
    """Upload once, copy the link, use it in custom CSS / HTML."""

    title = models.CharField(max_length=160, blank=True)
    file = models.FileField(upload_to="library/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "Media file"
        verbose_name_plural = "Media library"

    def __str__(self):
        return self.title or self.file.name.rsplit("/", 1)[-1]

    @property
    def is_image(self):
        return self.file.name.lower().rsplit(".", 1)[-1] in {"png", "jpg", "jpeg", "gif", "webp", "svg", "avif"}


class Inquiry(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Message"
        verbose_name_plural = "Inbox"

    def __str__(self):
        return f"{self.name} <{self.email}>"
