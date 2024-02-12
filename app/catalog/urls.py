from rest_framework_extensions.routers import NestedRouterMixin

from config.contrib.rest import RestRouter
from catalog.rest import TopicViewSet, CatalogEntryViewSet

api_router = RestRouter()
api_router.register(r'catalog/topics', TopicViewSet)
# api_router.register(r'catalog/entries', CatalogEntryViewSet)

class NestedRestRouter(NestedRouterMixin, RestRouter):
    pass

nested_router = NestedRestRouter()
(
nested_router.register(r'catalog/topics', TopicViewSet)
.register(
    r'entries',             # the url prefix
    CatalogEntryViewSet,
    'topic-entries',        # the url name
    parents_query_lookups=['topic_id']
)
)

api_router.registry.extend(nested_router.registry)
