"""apiproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from api.views import home
from django.conf.urls.static import static
from django.conf import settings
from custom_user.views import FacebookLogin, facebook_callback
from allauth.socialaccount.providers.facebook import views as facebook_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('api/', include('api.urls')),
    path('accounts/', include('allauth.urls')),  # for facebook login button
    path('rest-auth/facebook/', FacebookLogin.as_view(), name='fb_login'),
    path('auth/facebook/', facebook_callback, name='facebook_callback'),
    path('auth/github/url/', facebook_views.oauth2_login)
    # path(r'rest-auth/facebook/connect/', FacebookConnect.as_view(), name='fb_connect')
    # path('register/', include('custom_user.urls')),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
