from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('hello/', TemplateView.as_view(template_name='hello.html')),
    path('items/', include('item.urls')),
]
