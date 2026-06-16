from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Temporary dashboard preview - bypass login
    path(
        'login/',
        RedirectView.as_view(url='/'),
        name='login'
    ),

    path('', include('dashboard.urls')),
]
