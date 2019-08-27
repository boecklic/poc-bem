from layerservice.contrib.rest import RestRouter

from catalog.rest import TopicViewSet, CatalogEntryViewSet

api_router = RestRouter()
api_router.register(r'catalog/topics', TopicViewSet)
api_router.register(r'catalog/entries', CatalogEntryViewSet)