from django.contrib import admin
from django.urls import path, include
from dashboard import views

urlpatterns = [

    path("admin/", admin.site.urls),

    # Dashboard without login
    path("", views.home, name="home"),

    # Dashboard namespace
    path("", include("dashboard.urls")),
]