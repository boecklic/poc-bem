from layerservice.contrib.rest import RestRouter

from catalog.rest import TopicViewSet, CatalogEntryViewSet

api_router = RestRouter()
api_router.register(r'topics', TopicViewSet)
api_router.register(r'catalogentries', CatalogEntryViewSet)