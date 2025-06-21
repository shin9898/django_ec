from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('items/', include('item.urls')),
    path('', RedirectView.as_view(url='/items/', permanent=True)),  # ルートURLを/items/にリダイレクト
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
