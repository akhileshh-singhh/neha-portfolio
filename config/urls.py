from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

from cms import api, views as cms_views

admin.site.site_header = "Neha Varma · Website manager"
admin.site.site_title = "Website manager"
admin.site.index_title = "Dashboard"

urlpatterns = [
    path("admin/import-defaults/", cms_views.import_defaults, name="import_defaults"),
    path("admin/", admin.site.urls),
    path("api/site/", api.SiteView.as_view()),
    path("api/pages/", api.PageListView.as_view()),
    path("api/pages/<slug:slug>/", api.PageDetailView.as_view()),
    path("api/contact/", api.ContactAPIView.as_view()),
]

if settings.SERVE_MEDIA:
    urlpatterns += [re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT})]

urlpatterns += [path("", include("cms.urls"))]
