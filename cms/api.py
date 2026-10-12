from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .models import Page, SiteSettings, Theme
from .serializers import (InquirySerializer, PageListSerializer, PageSerializer,
                          SiteSettingsSerializer, ThemeSerializer)


class SiteView(APIView):
    """GET /api/site/  ->  site settings + theme (colours, fonts, css variables)."""

    def get(self, request):
        ctx = {"request": request}
        return Response({
            "settings": SiteSettingsSerializer(SiteSettings.load(), context=ctx).data,
            "theme": ThemeSerializer(Theme.load(), context=ctx).data,
        })


class PageListView(generics.ListAPIView):
    """GET /api/pages/"""
    queryset = Page.objects.filter(is_published=True)
    serializer_class = PageListSerializer
    pagination_class = None


class PageDetailView(generics.RetrieveAPIView):
    """GET /api/pages/<slug>/  (use 'home' alias for the home page)  ->  page with ordered sections + items."""
    serializer_class = PageSerializer
    lookup_field = "slug"
    queryset = Page.objects.filter(is_published=True)

    def get_object(self):
        if self.kwargs["slug"] == "home":
            page = Page.objects.filter(is_home=True, is_published=True).first()
            if page:
                self.check_object_permissions(self.request, page)
                return page
        return super().get_object()


class ContactAPIView(generics.CreateAPIView):
    """POST /api/contact/  {name, email, message}"""
    serializer_class = InquirySerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "contact"

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        self.perform_create(ser)
        return Response({"ok": True}, status=status.HTTP_201_CREATED)
