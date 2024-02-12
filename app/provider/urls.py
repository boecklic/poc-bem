from config.contrib.rest import RestRouter

from rest_framework_extensions.routers import NestedRouterMixin

from provider.api import ProviderViewSet

api_router = RestRouter()
api_router.register(r'providers', ProviderViewSet)

# Check http://chibisov.github.io/drf-extensions/docs/#nested-routes
# and https://medium.com/@EnterGodMode__/simple-nested-api-using-django-rest-framework-d2dd9f0ff093
# for details about nested routers
class NestedRestRouter(NestedRouterMixin, RestRouter):
    pass

nested_router = NestedRestRouter()
(
nested_router.register(r'providers', ProviderViewSet)
)

api_router.registry.extend(nested_router.registry)
