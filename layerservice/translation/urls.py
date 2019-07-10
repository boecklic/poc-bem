from rest_framework import routers

from translation.rest import TranslationKeyViewSet#, LayersJSViewViewSet

api_router = routers.DefaultRouter()
api_router.register(r'translations', TranslationKeyViewSet)
# api_router.register(r'config', LayersJSViewViewSet, basename='server_layername')