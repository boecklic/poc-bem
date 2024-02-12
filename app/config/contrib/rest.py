
from rest_framework import routers

class RestRouter(routers.SimpleRouter):

    def __init__(self, *args, trailing_slash=False, **kwargs):
        super().__init__(
            *args,
            trailing_slash=trailing_slash,
            **kwargs
        )