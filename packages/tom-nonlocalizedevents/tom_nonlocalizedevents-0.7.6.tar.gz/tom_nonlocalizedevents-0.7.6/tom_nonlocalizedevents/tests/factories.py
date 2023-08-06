import factory
# from datetime import datetime
from django.db.models import signals
from tom_nonlocalizedevents.models import NonLocalizedEvent, EventLocalization, EventSequence


class NonLocalizedEventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = NonLocalizedEvent

    event_id = factory.Faker('pystr')


class EventSequenceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EventSequence


@factory.django.mute_signals(signals.post_save)
class EventLocalizationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EventLocalization

    skymap_url = factory.Faker('pystr')
    date = factory.Faker('date_time')
