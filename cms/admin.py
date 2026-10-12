from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from django import forms
from django.contrib import admin, messages
from django.db import models
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.html import format_html, format_html_join

from .admin_ui import CONTENT_FIELDS, ITEM_FIELDS, KIND_UI, SLOT_LABELS, THEME_LIVE
from .models import Asset, Inquiry, Item, Page, Section, SiteSettings, Theme


# ---------------------------------------------------------------------------
# singletons: the "list" page jumps straight to the one editable row
# ---------------------------------------------------------------------------
class SingletonAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not self.model.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = self.model.load()
        return HttpResponseRedirect(reverse(f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change", args=[obj.pk]))


@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonAdmin):
    fieldsets = [
        ("Name, title & search engines", {
            "description": "How the website introduces itself: browser tab, Google results and link previews.",
            "fields": ["display_name", "site_title", "meta_description", "favicon", "share_image", "allow_search_engines"]}),
        ("Contact details", {
            "description": "Typed once here, used everywhere: the info row and the hire bar.",
            "fields": ["email", "phone", "linkedin_url"]}),
        ("Floating “available for hire” bar", {
            "description": "The small pill that floats at the bottom of every page.",
            "fields": ["bar_enabled", "bar_avatar_text", "bar_avatar_bg", "bar_message",
                       ("bar_primary_label", "bar_primary_url"), ("bar_secondary_label", "bar_secondary_url")]}),
        ("Advanced: tracking & custom code", {"classes": ["collapse"], "fields": ["head_html", "body_end_html"]}),
    ]
    change_form_template = "admin/cms/live_preview_form.html"

    def render_change_form(self, request, context, *args, **kwargs):
        context["preview_title"] = "How it looks now"
        context["preview_hint"] = "Reload after saving to see your changes. Scroll the preview to the bottom to see the floating bar."
        return super().render_change_form(request, context, *args, **kwargs)


@admin.register(Theme)
class ThemeAdmin(SingletonAdmin):
    fieldsets = [
        ("Core colours", {"description": "Change a colour and the preview on the right updates instantly (nothing is saved until you press Save).", "fields": [
            "color_black", "color_black_2", "color_text", "color_muted", "color_ink", "color_grey"]}),
        ("Palette colours (the coloured blocks)", {"fields": [
            "color_teal", "color_lime", "color_red", "color_olive", "color_gold", "color_accent"]}),
        ("Cards, placeholders & bar", {"fields": [
            "color_paper", "color_paper_text", "color_card_dark", "color_placeholder_from", "color_placeholder_to", "color_bar_bg"]}),
        ("Typography & layout", {"fields": ["font_family", "google_fonts_url", "base_font_size", "line_height", "container_width"]}),
        ("Scrolling strip", {"fields": ["ticker_seconds", "animate_ticker"]}),
        ("Custom CSS (advanced)", {"classes": ["collapse"], "fields": ["custom_css"]}),
    ]
    change_form_template = "admin/cms/live_preview_form.html"

    def render_change_form(self, request, context, *args, **kwargs):
        import json

        context["theme_live"] = THEME_LIVE
        context["preview_title"] = "Live preview"
        context["preview_hint"] = "Colours and sizes change here instantly while you type. Press Save to publish them."
        return super().render_change_form(request, context, *args, **kwargs)


# ---------------------------------------------------------------------------
# items inside a block
# ---------------------------------------------------------------------------
class ItemInline(SortableInlineAdminMixin, admin.StackedInline):
    model = Item
    extra = 0
    fields = ["slot", "visible", "title", "text", "image", "url", "bg_color", "text_color"]
    formfield_overrides = {
        models.TextField: {"widget": forms.Textarea(attrs={"rows": 2})},
    }
    verbose_name = "item"
    verbose_name_plural = "Items in this block"


@admin.register(Section)
class SectionAdmin(SortableAdminMixin, admin.ModelAdmin):
    inlines = [ItemInline]
    list_display = ["section_col", "kind_col", "page", "visible", "has_image", "updated_at"]
    list_display_links = ["section_col"]
    list_editable = ["visible"]
    list_filter = ["page", "kind", "visible"]
    search_fields = ["name", "heading", "subheading", "body"]
    actions = ["duplicate", "hide", "show"]
    readonly_fields = ["preview_link"]
    change_form_template = "admin/cms/section/change_form.html"
    change_list_template = "admin/cms/section/change_list.html"
    fieldsets = [
        ("What is this block?", {"fields": ["page", "kind", "name", "visible", "preview_link"]}),
        ("Text", {"fields": ["eyebrow", "heading", "subheading", "body", "footnote"]}),
        ("Image / video", {"fields": ["image", "image_alt", "placeholder_text", "video_file", "video_url"]}),
        ("Options", {"fields": ["ticker_text", "ticker_speed", "layout", "columns"]}),
        ("Design (only this block)", {"description": "Leave anything empty to keep the normal look of this block type.", "fields": [
            "bg_color", "text_color", "accent_color", "bg_gradient", "bg_image", "align",
            "padding_top", "padding_bottom", "min_height", "font_family"]}),
        ("Advanced", {"classes": ["collapse"], "fields": ["anchor_id", "css_class", "custom_css"]}),
    ]
    formfield_overrides = {
        models.TextField: {"widget": forms.Textarea(attrs={"rows": 3})},
    }

    # ---- list columns
    @admin.display(description="Block", ordering="name")
    def section_col(self, obj):
        ui = KIND_UI.get(obj.kind, {})
        excerpt = (obj.heading or obj.body or "").replace("\n", " ").replace("*", "").strip()[:70]
        return format_html(
            '<span class="blk"><span class="blk-ico">{}</span><span><b>{}</b><small>{}</small></span></span>',
            ui.get("icon", "▫️"), obj.name or obj.label, excerpt)

    @admin.display(description="Type", ordering="kind")
    def kind_col(self, obj):
        return KIND_UI.get(obj.kind, {}).get("name", obj.get_kind_display())

    @admin.display(boolean=True, description="Has image")
    def has_image(self, obj):
        return bool(obj.image or obj.bg_image)

    @admin.display(description="See it on the website")
    def preview_link(self, obj):
        if not obj.pk:
            return "Save once, then a live preview of this block appears on the right."
        base = "/" if obj.page.is_home else f"/preview/{obj.page.slug}/"
        return format_html('<a href="{}#{}" target="_blank">Open the page at this block ↗</a>', base, obj.dom_id)

    # ---- form: pass the plain-language config to the page script
    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context.update({
            "kind_ui": KIND_UI, "content_fields": CONTENT_FIELDS, "item_fields": ITEM_FIELDS, "slot_labels": SLOT_LABELS,
            "block_id": object_id,
        })
        if object_id:
            sec = Section.objects.filter(pk=object_id).first()
            extra_context["block_dom_id"] = sec.dom_id if sec else ""
        return super().changeform_view(request, object_id, form_url, extra_context)

    # ---- visual page map
    def get_urls(self):
        return [path("map/", self.admin_site.admin_view(self.page_map), name="cms_section_map")] + super().get_urls()

    def page_map(self, request):
        pages = list(Page.objects.all())
        current = None
        if request.GET.get("page"):
            current = next((p for p in pages if str(p.pk) == request.GET["page"]), None)
        current = current or next((p for p in pages if p.is_home), None) or (pages[0] if pages else None)
        blocks = list(current.sections.all()) if current else []
        for b in blocks:
            b.ui = KIND_UI.get(b.kind, {})
        ctx = {
            **self.admin_site.each_context(request),
            "title": "Page map", "opts": self.model._meta,
            "pages": pages, "current": current, "blocks": blocks,
        }
        return TemplateResponse(request, "admin/cms/page_map.html", ctx)

    # ---- actions
    @admin.action(description="Duplicate selected blocks")
    def duplicate(self, request, queryset):
        n = 0
        for sec in queryset:
            items = list(sec.items.all())
            sec.pk = None
            sec.name = (sec.name or sec.label) + " (copy)"
            sec.save()
            for it in items:
                it.pk = None
                it.section = sec
                it.save()
            n += 1
        self.message_user(request, f"Duplicated {n} block(s). The copies are at the end of the page.", messages.SUCCESS)

    @admin.action(description="Hide selected blocks")
    def hide(self, request, queryset):
        queryset.update(visible=False)

    @admin.action(description="Show selected blocks")
    def show(self, request, queryset):
        queryset.update(visible=True)


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ["title", "slug", "is_home", "is_published", "block_count", "updated_at"]
    list_filter = ["is_published"]
    prepopulated_fields = {"slug": ["title"]}
    readonly_fields = ["blocks_overview"]
    fieldsets = [
        ("Page", {"fields": ["title", "slug", "is_home", "is_published", "show_hire_bar"]}),
        ("Search engines & sharing", {"description": "Appears in Google results and when the page link is shared.", "fields": ["meta_title", "meta_description", "share_image"]}),
        ("Blocks on this page", {"fields": ["blocks_overview"]}),
    ]

    @admin.display(description="Blocks")
    def block_count(self, obj):
        return obj.sections.count()

    @admin.display(description="Top to bottom")
    def blocks_overview(self, obj):
        if not obj.pk:
            return "Save the page first, then add blocks."
        rows = format_html_join(
            "", '<li><a href="{}">{}</a> <small>{}{}</small></li>',
            (
                (reverse("admin:cms_section_change", args=[s.pk]), s.label, KIND_UI.get(s.kind, {}).get("name", s.get_kind_display()),
                 "" if s.visible else " · hidden")
                for s in obj.sections.all()
            ),
        )
        add = reverse("admin:cms_section_add") + f"?page={obj.pk}"
        pmap = reverse("admin:cms_section_map") + f"?page={obj.pk}"
        order = reverse("admin:cms_section_changelist") + f"?page__id__exact={obj.pk}"
        return format_html(
            '<ol class="blocks-ol">{}</ol><a class="button" href="{}">+ Add block</a> '
            '<a class="button" href="{}">🗺 Visual page map</a> <a class="button" href="{}">↕ Drag to re-order</a>', rows, add, pmap, order)


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ["thumb", "__str__", "link", "uploaded_at"]
    readonly_fields = ["link"]
    fields = ["title", "file", "link"]

    @admin.display(description="")
    def thumb(self, obj):
        if obj.is_image:
            return format_html('<img src="{}" style="height:42px;border-radius:6px">', obj.file.url)
        return "📄"

    @admin.display(description="Link to use in custom CSS / HTML")
    def link(self, obj):
        if not obj.pk:
            return "Upload to get the link."
        return format_html('<input readonly value="{}" style="width:28em" onclick="this.select()">', obj.file.url)


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "short", "created_at", "is_read"]
    list_filter = ["is_read"]
    list_editable = ["is_read"]
    search_fields = ["name", "email", "message"]
    readonly_fields = ["name", "email", "message", "created_at"]
    actions = ["mark_read"]

    def has_add_permission(self, request):
        return False

    @admin.display(description="Message")
    def short(self, obj):
        return obj.message[:70]

    @admin.action(description="Mark as read")
    def mark_read(self, request, queryset):
        queryset.update(is_read=True)
