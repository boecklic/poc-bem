from rest_framework import routers

from .serializers import DatasetViewSet, LayersJSViewViewSet

api_router = routers.DefaultRouter()
api_router.register(r'dataset', DatasetViewSet)
api_router.register(r'config', LayersJSViewViewSet, basename='server_layername')