from rest_framework import routers

from layers.rest import DatasetViewSet

api_router = routers.SimpleRouter()
api_router.register(r'layers/datasets', DatasetViewSet)
# api_router.register(r'catalogentries', CatalogEntryViewSet)