from django.conf.urls.static import static  # 追加
from django.contrib import admin
from django.urls import path, include

from . import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("forum/", include("main.urls")),
    path("accounts/", include("allauth.urls")),  # 追加
]

# 以下を追加
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
