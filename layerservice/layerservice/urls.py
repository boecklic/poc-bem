"""layerservice URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import include, path, re_path
from rest_framework import routers
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi



from bod_master.urls import api_router as bod_master_api_router
from catalog.urls import api_router as catalog_api_router
from translation.urls import api_router as translation_api_router
from layers.urls import api_router as layers_api_router

admin.site.site_header = 'Layer Service'

# check https://github.com/axnsan12/drf-yasg/ for details
# about drf_yasg (Yet another Swagger generator) for
# django-rest-framework
schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.swisstopo.ch/",
      contact=openapi.Contact(email="admin@swisstopo.ch"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

default_api_router = routers.DefaultRouter()
default_api_router.registry.extend(catalog_api_router.registry)
default_api_router.registry.extend(translation_api_router.registry)
default_api_router.registry.extend(layers_api_router.registry)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('tst/', include('tst.urls')),
    re_path('api/v3/doc/swagger(?P<format>\.json|\.yaml)', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('api/v3/doc/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/v3/doc/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/v3/', include(default_api_router.urls)),
    # path('api/v3/', include((catalog_api_router.urls, 'catalog'), namespace='catalog')),
    # path('api/v3/', include((translation_api_router.urls, 'translation'), namespace='translation')),
    # path('api/v3/', include((layers_api_router.urls, 'layers'), namespace='layers')),
]
