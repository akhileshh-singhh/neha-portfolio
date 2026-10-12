from django.urls import path

from . import views

app_name = "cms"

urlpatterns = [
    path("", views.home, name="home"),
    path("contact/send/", views.contact_submit, name="contact"),
    path("robots.txt", views.robots_txt, name="robots"),
    path("sitemap.xml", views.sitemap_xml, name="sitemap"),
    path("preview/<slug:slug>/", views.preview, name="preview"),
    path("block-preview/<int:pk>/", views.block_preview, name="block_preview"),
    path("<slug:slug>/", views.page_detail, name="page"),
]
