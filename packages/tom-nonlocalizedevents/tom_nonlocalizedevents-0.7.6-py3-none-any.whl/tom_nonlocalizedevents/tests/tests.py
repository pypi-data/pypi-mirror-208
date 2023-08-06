from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase

from tom_nonlocalizedevents.tests.factories import (NonLocalizedEventFactory, EventLocalizationFactory,
                                                    EventSequenceFactory)


class NonLocalizedEventAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_user')
        self.superevent1 = NonLocalizedEventFactory.create(event_id='superevent1')
        self.superevent2 = NonLocalizedEventFactory.create(event_id='superevent2')
        self.eventlocalization1 = EventLocalizationFactory.create(nonlocalizedevent=self.superevent1)
        self.eventlocalization2 = EventLocalizationFactory.create(nonlocalizedevent=self.superevent2)
        self.sequence11 = EventSequenceFactory.create(
            nonlocalizedevent=self.superevent1, localization=self.eventlocalization1
        )
        self.sequence21 = EventSequenceFactory.create(
            nonlocalizedevent=self.superevent2, localization=self.eventlocalization2
        )
        self.client.force_login(self.user)


class TestNonLocalizedEventViewSet(NonLocalizedEventAPITestCase):

    def test_nonlocalizedevent_list_api(self):
        """Test NonLocalizedEvent API list endpoint."""
        response = self.client.get(reverse('api:nonlocalizedevent-list'))

        self.assertEqual(response.json()['count'], 2)
        self.assertContains(response, f'"event_id":"{self.superevent1.event_id}"')
        self.assertContains(response, f'"skymap_url":"{self.eventlocalization1.skymap_url}"')
        self.assertContains(response, f'"event_id":"{self.superevent2.event_id}"')
        self.assertContains(response, f'"skymap_url":"{self.eventlocalization2.skymap_url}"')

    def test_nonlocalizedevent_index_view(self):
        response = self.client.get(reverse('nonlocalizedevents:index'))

        self.assertContains(response, self.superevent1.event_id)
        self.assertContains(response, self.superevent2.event_id)
        self.assertContains(response, reverse('nonlocalizedevents:detail', args=(self.superevent1.pk,)))
        self.assertContains(response, reverse('nonlocalizedevents:detail', args=(self.superevent2.pk,)))

    def test_superevent_detail_view(self):
        response = self.client.get(reverse('nonlocalizedevents:detail', args=(self.superevent1.pk,)))

        self.assertContains(response, self.superevent1.event_id)
        self.assertContains(response, "superevent-sequences")
        self.assertContains(response, "vue")


class TestEventLocalizationViewSet(NonLocalizedEventAPITestCase):
    def test_eventlocalization_list(self):
        """Test EventLocalization API list endpoint."""
        response = self.client.get(reverse('api:eventlocalization-list'))

        self.assertEqual(response.json()['count'], 2)
