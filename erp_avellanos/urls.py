from django.contrib import admin
from django.urls import path
from erp_app.admin import custom_admin_site  # ← importante

urlpatterns = [
    path('admin/', custom_admin_site.urls),  # ← usa custom_admin_site, no admin.site
]