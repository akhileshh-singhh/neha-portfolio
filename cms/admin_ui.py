"""Plain-language description of every block type.

The admin uses this to (1) show only the fields that block actually uses,
(2) rename them to what they look like on the website, and (3) explain where each one appears.
It is sent to the browser as JSON (see templates/admin/cms/section/change_form.html).
"""

F = lambda label, hint="": {"label": label, "hint": hint}  # noqa: E731
EM = "Enter = new line · *word* = italic · **word** = bold"

KIND_UI = {
    "title": {
        "icon": "🏷️", "name": "Title banner",
        "where": "The very first block of the page: two rows of slashes, your big italic title and your handle.",
        "fields": {
            "eyebrow": F("Top row of slashes", "The line of / characters above the title."),
            "heading": F("Big title", EM),
            "subheading": F("Handle line", "Small line under the title, e.g. your @instagram handle."),
            "footnote": F("Bottom row of slashes", "The line of / characters under the handle."),
        },
    },
    "info": {
        "icon": "🪪", "name": "Info row",
        "where": "The dark card with your name, two portrait photos, email/phone and the giant word. Your name, LinkedIn link, email and phone come from Site settings.",
        "fields": {
            "eyebrow": F("Year (top middle)", "e.g. 2026"),
            "subheading": F("Top-right text", "e.g. “Let's see my work!”"),
            "heading": F("Giant word", "The huge word across the bottom, e.g. Creative."),
            "footnote": F("Tiny corner text (optional)", "Appears at the bottom-right of the card."),
        },
        "items": {"label": "Portrait photos", "hint": "Add up to 2 photos. The first is the bigger one.", "default_slot": "photo",
                  "fields": {"image": F("Photo", "Portrait, 3:4 works best."), "title": F("Label shown on the empty box", "Only visible until a photo is uploaded.")}},
    },
    "bring": {
        "icon": "✨", "name": "What I bring",
        "where": "Three columns: statements on the left, a photo in the middle, statements + platform pills on the right.",
        "fields": {
            "heading": F("Block title", "Centred at the top of the block."),
            "image": F("Centre photo", "Appears between the two text columns."),
            "image_alt": F("Photo description", "For accessibility / Google."),
            "placeholder_text": F("Empty-photo label", "Shown in the grey box until you upload a photo."),
            "subheading": F("Label above the pills", "e.g. Platforms"),
            "footnote": F("Text at the very bottom", "Optional centred line."),
        },
        "items": {"label": "Statements & pills", "hint": "Choose where each one goes: left column, right column, or a platform pill.", "slots": ["left", "right", "chip"],
                  "fields": {"title": F("Text", "One statement or one pill (e.g. Instagram).")}},
    },
    "services": {
        "icon": "📋", "name": "Services list",
        "where": "Big numbered rows (heading on the left, small description on the right) with an optional scrolling strip underneath.",
        "fields": {
            "ticker_text": F("Scrolling strip text", "Repeats across the grey strip under the list. Leave empty for no strip."),
            "ticker_speed": F("Strip speed (seconds)", "Time for one loop. Empty = theme default."),
        },
        "items": {"label": "Rows", "hint": "One row per service.", "fields": {
            "title": F("Row heading", "Big text on the left, e.g. “1. content strategy.”"),
            "text": F("Row description", "Small uppercase text on the right.")}},
    },
    "rows": {
        "icon": "📑", "name": "Plain list rows",
        "where": "The same big-heading + description rows, used for “skills.” and “studies.”.",
        "fields": {},
        "items": {"label": "Rows", "hint": "One row per entry.", "fields": {
            "title": F("Row heading", "Big text on the left, e.g. “skills.”"),
            "text": F("Row description", "Small uppercase text on the right.")}},
    },
    "fullbleed": {
        "icon": "🏞️", "name": "Full-width banner",
        "where": "A tall banner with text on a background. Set the picture or gradient in the Design box below.",
        "fields": {"heading": F("Text on the banner", EM)},
    },
    "caption": {
        "icon": "💬", "name": "Caption bar",
        "where": "A slim bar of text, normally right under a banner.",
        "fields": {"heading": F("Bold first line", ""), "body": F("Description", "The normal text after the bold line.")},
    },
    "video": {
        "icon": "🎬", "name": "Video",
        "where": "A 16:9 video player. Until you add a video it shows a grey box with the label.",
        "fields": {
            "heading": F("Label on the empty box", "Shown only while there is no video."),
            "subheading": F("Caption under the video", ""),
            "image": F("Poster image", "Shown before the video plays."),
            "video_file": F("Upload a video file", "mp4 / webm / mov."),
            "video_url": F("…or paste a link", "YouTube, Vimeo or direct .mp4 link. Used if no file is uploaded."),
        },
    },
    "statement": {
        "icon": "📣", "name": "Big statement",
        "where": "A coloured band with giant text and a small italic line.",
        "fields": {"heading": F("Giant text", EM), "subheading": F("Small italic line", "Under the giant text.")},
    },
    "photos": {
        "icon": "🖼️", "name": "Photo grid",
        "where": "A set of photos. Pair = two tall photos on a coloured band; Mosaic = first photo wide; Grid = equal squares.",
        "fields": {"layout": F("Arrangement", ""), "columns": F("Columns (grid only)", "How many squares per row.")},
        "layouts": [["pair", "Pair (two tall photos)"], ["mosaic", "Mosaic (first one wide)"], ["grid", "Grid (equal squares)"]],
        "items": {"label": "Photos", "hint": "Upload one image per photo box.", "fields": {
            "image": F("Photo", ""), "title": F("Label on the empty box", "Shown only until a photo is uploaded.")}},
    },
    "feature": {
        "icon": "🍽️", "name": "Photo + headline",
        "where": "One photo beside a headline, on a coloured background.",
        "fields": {
            "heading": F("Headline", EM), "subheading": F("Small line under the headline", ""),
            "image": F("Photo", ""), "image_alt": F("Photo description", ""), "placeholder_text": F("Empty-photo label", ""),
            "layout": F("Photo side", ""),
        },
        "layouts": [["", "Photo on the left"], ["image-right", "Photo on the right"]],
    },
    "brand": {
        "icon": "⭕", "name": "Brand intro",
        "where": "A round logo with the brand name, tagline and a short paragraph.",
        "fields": {
            "eyebrow": F("Text inside the round logo", "e.g. 88. Ignored if you upload a logo image."),
            "image": F("Logo image (optional)", "Replaces the text in the circle."), "image_alt": F("Logo description", ""),
            "heading": F("Brand name", ""), "subheading": F("Tagline", ""),
            "body": F("Paragraph", "**bold** works."),
        },
    },
    "case_study": {
        "icon": "📈", "name": "Case study",
        "where": "A card with a mockup image on the left and Goal / Strategy / Result on the right.",
        "fields": {
            "heading": F("Case title", ""), "image": F("Mockup image", ""), "image_alt": F("Image description", ""),
            "placeholder_text": F("Empty-image label", ""), "footnote": F("Small line under the results", "e.g. client, role, years."),
            "layout": F("Card colour", ""),
        },
        "layouts": [["", "Light card"], ["dark", "Dark card"]],
        "items": {"label": "Goal / Strategy / Result rows", "hint": "Each row is one bold label followed by a sentence.", "default_slot": "row", "fields": {
            "title": F("Bold label", "Goal, Strategy or Result."), "text": F("Sentence", "")}},
    },
    "tiles": {
        "icon": "🟩", "name": "Colour tiles",
        "where": "Big square tiles, each with one word on its own colour.",
        "fields": {"columns": F("Tiles per row", "Default 3.")},
        "items": {"label": "Tiles", "hint": "One tile per word.", "fields": {
            "title": F("Word on the tile", ""), "url": F("Link (optional)", ""),
            "bg_color": F("Tile colour", ""), "text_color": F("Word colour", "")}},
    },
    "label": {
        "icon": "🔖", "name": "Section label",
        "where": "A big word with a small line under it, used to introduce the next group of blocks.",
        "fields": {"heading": F("Big word", ""), "subheading": F("Small line", "")},
    },
    "stats": {
        "icon": "🔢", "name": "Role + numbers",
        "where": "A coloured block with a role title, a paragraph and big result numbers.",
        "fields": {
            "heading": F("Title", ""), "subheading": F("Role line", "Smaller text under the title."),
            "body": F("Paragraph", ""), "columns": F("Numbers per row", "Default 3."),
        },
        "items": {"label": "Big numbers", "hint": "One per statistic.", "fields": {
            "title": F("Big number", "e.g. 114%"), "text": F("Caption", "e.g. admission growth")}},
    },
    "promo": {
        "icon": "📐", "name": "Text + mockup",
        "where": "A heading and paragraph on the left, a tall mockup image on the right.",
        "fields": {
            "heading": F("Heading", ""), "body": F("Paragraph", ""), "image": F("Mockup image", ""),
            "image_alt": F("Image description", ""), "placeholder_text": F("Empty-image label", ""),
        },
    },
    "closing": {
        "icon": "👍", "name": "Closing block",
        "where": "The last block: an emoji badge, a small title and a row of thumbnails.",
        "fields": {
            "eyebrow": F("Emoji in the round badge", "e.g. 👍"), "heading": F("Small title", ""),
            "subheading": F("Line under the title", "e.g. Published: October 2026"),
        },
        "items": {"label": "Thumbnails", "hint": "Small boxes in a scrolling row.", "fields": {
            "image": F("Thumbnail image", ""), "title": F("Label on the empty box", ""), "bg_color": F("Box colour", "")}},
    },
    "contact_form": {
        "icon": "✉️", "name": "Contact form",
        "where": "A name / email / message form. Messages land in the Inbox.",
        "fields": {"heading": F("Heading", ""), "body": F("Text above the form", ""), "subheading": F("Button label", "Default: Send message")},
    },
    "custom_html": {
        "icon": "🧩", "name": "Custom HTML",
        "where": "Anything you can write in HTML, placed exactly as typed. For experts.",
        "fields": {"body": F("HTML code", "Pasted as-is. Only paste code you trust.")},
    },
    "spacer": {
        "icon": "↕️", "name": "Spacer",
        "where": "Empty vertical space between blocks.",
        "fields": {},
        "note": "Set the height with “Min height” in the Design box.",
    },
}

# every content field the form knows about (anything not listed for a block type is hidden)
CONTENT_FIELDS = [
    "eyebrow", "heading", "subheading", "body", "footnote", "image", "image_alt", "placeholder_text",
    "video_file", "video_url", "ticker_text", "ticker_speed", "layout", "columns",
]
ITEM_FIELDS = ["slot", "title", "text", "image", "url", "bg_color", "text_color"]
SLOT_LABELS = {"photo": "Photo", "left": "Left column", "right": "Right column", "chip": "Platform pill", "row": "Result row"}

# Theme: form field -> CSS variable (for the live preview)
THEME_LIVE = {
    "id_color_black": "--k", "id_color_black_2": "--k2", "id_color_text": "--w", "id_color_muted": "--m",
    "id_color_grey": "--grey", "id_color_teal": "--teal", "id_color_lime": "--lime", "id_color_red": "--red",
    "id_color_olive": "--olive", "id_color_gold": "--gold", "id_color_ink": "--ink", "id_color_paper": "--paper",
    "id_color_paper_text": "--paper-ink", "id_color_card_dark": "--card-dark", "id_color_placeholder_from": "--ph1",
    "id_color_placeholder_to": "--ph2", "id_color_bar_bg": "--bar-bg", "id_color_accent": "--accent",
    "id_font_family": "--font", "id_base_font_size": "--fs|px", "id_line_height": "--lh",
    "id_container_width": "--maxw|px", "id_ticker_seconds": "--ticker|s",
}
