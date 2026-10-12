"""Built-in default content = the current static website (nehahaportfolio.netlify.app).

Used in two places:
* the public site falls back to it whenever the database has no page (or no database at all);
* `manage.py seed_site` / the admin "Import default content" button copy it into the database
  so it becomes editable.
"""
import copy

SLASHES = "////////////////////////////"


def S(kind, name, **kw):
    items = kw.pop("items", [])
    return dict(kind=kind, name=name, items=items, **kw)


def I(title="", text="", slot="", **kw):
    return dict(title=title, text=text, slot=slot, **kw)


HOME = [
    S("title", "Title banner", eyebrow=SLASHES, heading="Social Media. Strategy. Creative",
      subheading="@nehahahahhah", footnote=SLASHES),
    S("info", "Intro & contact", eyebrow="2026", subheading="Let's see my work!", heading="Creative",
      items=[I(slot="photo"), I(slot="photo")]),
    S("bring", "What I bring", heading="What I bring to the table.", subheading="Platforms",
      items=[
          I("Turning ideas into concept-led social campaigns.", slot="left"),
          I("Short-form content // reels and stories.", slot="left"),
          I("Planning calendars and translating briefs into real posts.", slot="left"),
          I("Creating content // Photo and video.", slot="right"),
          I("Creating end-to-end projects, from brief to launch.", slot="right"),
          I("Social Media Design.", slot="right"),
          *[I(p, slot="chip") for p in ["Instagram", "Facebook", "YouTube", "Pinterest", "LinkedIn"]],
      ]),
    S("services", "Services list", ticker_text="02. social media.", items=[
        I("1. content strategy.", "Defined social media strategy, audience insights and a clear tone of voice to build a consistent digital presence."),
        I("2. social media.", "Content calendars, community management and lead conversations across Instagram, Facebook and YouTube."),
        I("3. photo and video.", "Reels, stories and short-form video content for products, services and events, made in Canva."),
        I("4. 88 Digital.", "Current role: planning, content and campaign delivery for client brands."),
    ]),
    S("fullbleed", "Goa resort banner", heading="Your *luxury* escape in Goa.",
      bg_gradient="linear-gradient(90deg,#6b4a2c,#2d1d12 70%,#1a1109)"),
    S("caption", "Goa resort caption", heading="The Palm Court Resort",
      body="Photo and video content, captions and a launch-week content calendar. Sample project."),
    S("video", "Short-form video", heading="short-form video final result", subheading="// short-form video final result"),
    S("statement", "Sundown Cafe", heading="Sundown Cafe", subheading="sip, chill, repeat."),
    S("photos", "Cafe photos", layout="pair", items=[I(), I()]),
    S("feature", "Mumbai restaurant", heading="Taste *Mumbai*\nin every bite.", subheading="Sample restaurant campaign"),
    S("brand", "88 Digital", eyebrow="88", heading="88 Digital", subheading="Strategy - Vision - Creativity",
      body="**88 Digital** helps brands grow online with strategy, content and campaigns built on adaptation, intuition and clear goals."),
    S("case_study", "Case: dance academy", heading="Dance and music academy", placeholder_text="Add mockup",
      footnote="SoundKraft DJ Academy, Marketing and CRM Executive, 2025 to 2026", items=[
          I("Goal", "grow admissions and bring cold leads back.", "row"),
          I("Strategy", "consistent content across Instagram, Facebook and YouTube, with structured follow-ups for every lead.", "row"),
          I("Result", "114% admission growth and a 17% dead-lead conversion rate.", "row")]),
    S("case_study", "Case: home decor", heading="Home decor and interior styling brand", placeholder_text="Add mockup", items=[
        I("Goal", "increase sales and strengthen brand awareness.", "row"),
        I("Strategy", "exclusive reels and carousel content, supported by stories that highlight new arrivals and trends, along with influencer collaborations.", "row"),
        I("Result", "increased sales, follower growth and overall reach. (Sample)", "row")]),
    S("case_study", "Case: fitness", heading="Fitness equipment brand", placeholder_text="Add mockup", layout="dark", items=[
        I("Goal", "increase brand awareness and boost sales.", "row"),
        I("Strategy", "reels showcasing product details, carousels highlighting features, and real-life user content and testimonials.", "row"),
        I("Result", "increased sales, follower growth, higher views and more inquiries. (Sample)", "row")]),
    S("tiles", "post / reel / story", items=[
        I("post.", bg_color="var(--lime)"), I("reel.", bg_color="#1a5cff", text_color="#ffffff"), I("story.", bg_color="#ff2d8a")]),
    S("photos", "Photo mosaic", layout="mosaic", items=[I(), I(), I(), I(), I()]),
    S("label", "Photo label", heading="photo.", subheading="my content journey"),
    S("video", "Reels highlights", heading="reels highlights.", subheading="reels highlights."),
    S("stats", "SoundKraft role", heading="SoundKraft DJ Academy", subheading="Marketing and CRM Executive",
      body="Managed content calendars, researched content ideas from audience insights and trends, and handled audience interactions and lead communication.",
      items=[I("114%", "admission growth"), I("17%", "dead-lead conversion"), I("3", "platforms managed")]),
    S("promo", "Templates", heading="Templates",
      body="Content pillars, visual consistency, monthly calendar, launch planning, production and growth strategy."),
    S("rows", "Skills & studies", items=[
        I("skills.", "Social media marketing, Instagram marketing, digital marketing, content strategy, market research, content creation, CRM operations, content calendar management, Canva."),
        I("studies.", "BMS Finance, Prahaladrai Dalmia Lions College, 2021 to 2024. Google Digital Marketing and E-Commerce, PwC Data Driven Decision Making, HubSpot SEO basics.")]),
    S("closing", "Closing", eyebrow="\U0001F44D", heading="CREATIVE PORTFOLIO", subheading="Published: October 2026",
      items=[I("", bg_color="var(--lime)"), I("Add"), I("Add"), I("Add"), I("Add")]),
]


def default_home_spec():
    """A fresh deep copy so callers may mutate it."""
    return copy.deepcopy(HOME)


def build_default_page():
    """Unsaved Page + Section/Item objects (never touches the database)."""
    from .models import Item, Page, Section

    page = Page(title="Home", slug="home", is_home=True, is_published=True)
    sections = []
    for n, spec in enumerate(default_home_spec(), start=1):
        items = spec.pop("items")
        sec = Section(page=page, order=n, **spec)
        sec.pk = -n  # fake ids so #block-<id> anchors still work
        sec.vis_items = [Item(order=m, section=sec, **it) for m, it in enumerate(items, start=1)]
        sections.append(sec)
    return page, sections
