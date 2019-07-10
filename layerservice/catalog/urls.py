from rest_framework import routers

from catalog.rest import TopicViewSet, CatalogEntryViewSet

api_router = routers.DefaultRouter()
api_router.register(r'catalog/topics', TopicViewSet)
api_router.register(r'catalog/catalogentries', CatalogEntryViewSet)