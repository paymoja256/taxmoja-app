"""_keenthemes URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import include, path
from django.conf import settings
from _keenthemes.views import SystemView
from django.conf.urls.static import static

from rest_framework import routers, serializers, viewsets
from django.contrib.auth.models import User


#  Rest Framework Classes


# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["url", "username", "email", "is_staff"]


# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r"users", UserViewSet)


urlpatterns = [
    path("admin/", admin.site.urls),
    # Dashboard urls
    path("", include("dashboards.urls")),
    # Auth urls
    path("", include("auth.urls")),
    # Rest Framework
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
    # Taxmoja urls
    path("xero/", include(("api_xero.urls", "xero"), namespace="xero")),
    path("dear/", include(("api_dear.urls", "dear"), namespace="dear")),
    path(
        "quickbooks/",
        include(("api_quickbooks.urls", "quickbooks"), namespace="quickbooks"),
    ),
    path(
        "oe/",
        include(("api_ordereasy.urls", "quickbooks"), namespace="ordereasy"),
    ),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = "Taxmoja Admin"
admin.site.site_title = "Taxmoja Admin Portal"
admin.site.index_title = "Welcome to Taxmoja Admin Portal"

handler404 = SystemView.as_view(template_name="pages/system/not-found.html", status=404)
handler500 = SystemView.as_view(template_name="pages/system/error.html", status=500)
