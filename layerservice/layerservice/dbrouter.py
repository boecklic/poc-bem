from bod_master.models import (LayersJS, LayersJSView, Topic,
    Catalog, XTDatasetCatalog, XTDatasetTopic)

RE3_MODELS = [LayersJS,
    LayersJSView,
    Topic,
    Catalog,
    XTDatasetTopic,
    XTDatasetCatalog
]

class SchemaEnabledDBRouter(object):
	# inspired by https://stackoverflow.com/a/51007441/9896222

    def db_for_read(self, model, **hints):
        if model in RE3_MODELS:
            return 're3'
        return None

    def db_for_write(self, model, **hints):
        if model in RE3_MODELS:
            return 're3'
        return None