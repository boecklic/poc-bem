from rest_framework import routers

from .serializers import BODDatasetViewSet, LayersJSViewViewSet

api_router = routers.DefaultRouter()
api_router.register(r'dataset', BODDatasetViewSet)
api_router.register(r'config', LayersJSViewViewSet, basename='server_layername')
