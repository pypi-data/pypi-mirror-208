from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings as django_settings
from django.conf.urls.static import static

from . import views
import django_cloudspotlicense.views as auth_views

urlpatterns = [
    path('select-company', auth_views.SelectCompanyView.as_view(), name='select_company'),
    path('set-company/<uuid:company_id>', auth_views.SetCompanyView.as_view(), name='set_company'),
    path('webhook', auth_views.WebhookView.as_view(), name='webhook'),
    path('impersonation', auth_views.ImpersonationCheckView.as_view(), name='impersonation-check'),
    path('impersonation/<slug:token>', auth_views.ImpersonationView.as_view(), name='impersonation-setup'),
]

# Serving media files in development
if django_settings.DEBUG is True:
    urlpatterns += static(django_settings.MEDIA_URL, document_root=django_settings.MEDIA_ROOT)
    urlpatterns += static(django_settings.STATIC_URL, document_root=django_settings.STATIC_ROOT)