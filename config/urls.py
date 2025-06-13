from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from django.views.generic.base import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('hello/', TemplateView.as_view(template_name='hello.html')),
    path('', include('item.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
