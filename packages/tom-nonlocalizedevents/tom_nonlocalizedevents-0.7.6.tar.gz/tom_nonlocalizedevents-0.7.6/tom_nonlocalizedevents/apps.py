from django.apps import AppConfig


class NonLocalizedEventTypesConfig(AppConfig):
    name = 'tom_nonlocalizedevents'

    def ready(self):
        import tom_nonlocalizedevents.signals.handlers  # noqa
        super().ready()
