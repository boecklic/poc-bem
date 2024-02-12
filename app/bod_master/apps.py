from django.apps import AppConfig


class BodMasterConfig(AppConfig):
    name = 'bod_master'
    # Note: this setting is just to mitigate the corresponding warning
    # all models in this app are unmanaged
    default_auto_field = 'django.db.models.AutoField'

