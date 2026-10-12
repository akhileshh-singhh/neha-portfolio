import re

from django import forms
from django.utils.html import format_html

_HEX = re.compile(r"^#[0-9a-fA-F]{6}$")


class ColorPickerWidget(forms.TextInput):
    """Text box (accepts any CSS colour) + native colour picker kept in sync."""

    def render(self, name, value, attrs=None, renderer=None):
        value = value or ""
        picker = value if _HEX.match(value) else "#000000"
        attrs = dict(attrs or {})
        attrs.setdefault("class", "vTextField")
        attrs["style"] = "width:14em"
        attrs["placeholder"] = "default"
        attrs["oninput"] = "this.previousElementSibling.value=/^#[0-9a-fA-F]{6}$/.test(this.value)?this.value:this.previousElementSibling.value"
        text = super().render(name, value, attrs, renderer)
        return format_html(
            '<span class="cms-color"><input type="color" value="{}" '
            'oninput="this.nextElementSibling.value=this.value" style="vertical-align:middle;width:2.4em;height:2em;padding:0;border:1px solid #bbb;border-radius:4px"> {} '
            '<a href="#" title="Reset to default" onclick="var t=this.previousElementSibling;t.value=\'\';return false;" style="margin-left:.4em">reset</a></span>',
            picker, text,
        )
