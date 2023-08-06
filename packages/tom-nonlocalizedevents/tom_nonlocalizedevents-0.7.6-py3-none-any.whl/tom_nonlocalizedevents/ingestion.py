import logging
import requests
import traceback

from tom_nonlocalizedevents.healpix_utils import create_localization_for_skymap
from tom_nonlocalizedevents.models import NonLocalizedEvent, EventSequence, ExternalCoincidence


logger = logging.getLogger(__name__)


def ingest_sequence_from_hermes_message(message):
    event_id = message.get('message', {}).get('data', {}).get('superevent_id', None)
    if not event_id:
        logger.warn(f"Got a malformed HermesBroker message, cannot created nonlocalizedevent. Message = {message}")
        return

    data = message.get('message', {}).get('data', {})

    if data.get('alert_type', '') == 'RETRACTION':
        NonLocalizedEvent.objects.update_or_create(
            event_id=event_id,
            event_type=NonLocalizedEvent.NonLocalizedEventType.GRAVITATIONAL_WAVE,
            defaults={'state': NonLocalizedEvent.NonLocalizedEventState.RETRACTED}
        )
        return

    nonlocalizedevent, nle_created = NonLocalizedEvent.objects.get_or_create(
        event_id=event_id,
        event_type=NonLocalizedEvent.NonLocalizedEventType.GRAVITATIONAL_WAVE,
    )
    if nle_created:
        logger.info(f"Ingested a new GW event with id {event_id} from HermesBroker")

    localization = None
    skymap_url = data.get('urls', {}).get('skymap')
    if skymap_url:
        try:
            skymap_resp = requests.get(skymap_url)
            skymap_resp.raise_for_status()
            localization = create_localization_for_skymap(
                nonlocalizedevent=nonlocalizedevent,
                skymap_bytes=skymap_resp.content,
                skymap_url=skymap_url
            )
        except Exception as e:
            localization = None
            logger.error(
                f"Failed to retrieve and process localization from skymap file at {skymap_url}. Exception: {e}"
            )
            logger.error(traceback.format_exc())

    combined_skymap_url = data.get('urls', {}).get('combined_skymap')
    external_coincidence = None
    if combined_skymap_url:
        try:
            combined_skymap_resp = requests.get(combined_skymap_url)
            combined_skymap_resp.raise_for_status()
            combined_localization = create_localization_for_skymap(
                nonlocalizedevent=nonlocalizedevent,
                skymap_bytes=combined_skymap_resp.content,
                skymap_url=combined_skymap_url,
                is_combined=True
            )
            external_coincidence, _ = ExternalCoincidence.objects.get_or_create(
                localization=combined_localization,
                defaults={'details': data.get('external_coinc')}
            )
        except Exception as e:
            combined_localization = None
            logger.error((
                f"Failed to retrieve and process combined localization from combined skymap file at"
                f"{combined_skymap_url}. Exception: {e}"
            ))
            logger.error(traceback.format_exc())

    # Now ingest the sequence for that event
    sequence_number = data.get('sequence_num')
    event_sequence, es_created = EventSequence.objects.update_or_create(
        nonlocalizedevent=nonlocalizedevent,
        localization=localization,
        external_coincidence=external_coincidence,
        sequence_id=sequence_number,
        details=data.get('event'),
        defaults={
            'event_subtype': data.get('alert_type'),
            'ingestor_source': 'hop'
        }
    )
    if es_created and localization is None:
        warning_msg = (
            f'{"Creating" if es_created else "Updating"} EventSequence without EventLocalization:'
            f'{event_sequence} for NonLocalizedEvent: {nonlocalizedevent}'
        )
        logger.warning(warning_msg)
