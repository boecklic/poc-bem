from layerservice.contrib.rest import RestRouter

from translation.rest import TranslationViewSet#, LayersJSViewViewSet

api_router = RestRouter()
api_router.register(r'translations', TranslationViewSet)
# api_router.register(r'config', LayersJSViewViewSet, basename='server_layername')