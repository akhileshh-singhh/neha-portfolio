from rest_framework import serializers

from .models import Inquiry, Item, Page, Section, SiteSettings, Theme


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ["id", "slot", "title", "text", "image", "url", "bg_color", "text_color"]


class SectionSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = Section
        exclude = ["page", "custom_css", "updated_at", "visible"]

    def get_items(self, obj):
        items = getattr(obj, "vis_items", None)
        if items is None:
            items = obj.items.filter(visible=True)
        return ItemSerializer(items, many=True, context=self.context).data


class PageSerializer(serializers.ModelSerializer):
    sections = serializers.SerializerMethodField()

    class Meta:
        model = Page
        fields = ["id", "title", "slug", "is_home", "meta_title", "meta_description", "share_image",
                  "show_hire_bar", "updated_at", "sections"]

    def get_sections(self, obj):
        from .views import _sections

        return SectionSerializer(_sections(obj), many=True, context=self.context).data


class PageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ["id", "title", "slug", "is_home", "updated_at"]


class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        exclude = ["id"]


class ThemeSerializer(serializers.ModelSerializer):
    css_variables = serializers.SerializerMethodField()

    class Meta:
        model = Theme
        exclude = ["id"]

    def get_css_variables(self, obj):
        return obj.css_variables()


class InquirySerializer(serializers.ModelSerializer):
    website = serializers.CharField(write_only=True, required=False, allow_blank=True)  # honeypot

    class Meta:
        model = Inquiry
        fields = ["name", "email", "message", "website"]

    def create(self, validated_data):
        if validated_data.pop("website", ""):
            return Inquiry(**validated_data)  # silently drop bots
        return super().create(validated_data)
