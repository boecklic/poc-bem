from layerservice.contrib.rest import RestRouter

from rest_framework_extensions.routers import NestedRouterMixin

from layers.rest import DatasetViewSet, MapServerLayerViewSet

api_router = RestRouter()
api_router.register(r'datasets', DatasetViewSet)
# api_router.register(r'mapfiles', MapServerConfigViewSet)
# api_router.register(r'catalogentries', CatalogEntryViewSet)

# Check http://chibisov.github.io/drf-extensions/docs/#nested-routes
# and https://medium.com/@EnterGodMode__/simple-nested-api-using-django-rest-framework-d2dd9f0ff093
# for details about nested routers
class NestedRestRouter(NestedRouterMixin, RestRouter):
    pass

nested_router = NestedRestRouter()
(
nested_router.register(r'datasets', DatasetViewSet)
.register(
    r'mapserverlayers',
    MapServerLayerViewSet,
    'dataset-mapserverlayers',
    parents_query_lookups=['group__dataset__name']
)
)