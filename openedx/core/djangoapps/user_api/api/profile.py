"""Python API for user profiles.

Profile information includes a student's demographic information and preferences,
but does NOT include basic account information such as username, password, and
email address.

"""
import datetime
import logging

from django.conf import settings
from django.db import IntegrityError
from pytz import UTC
import analytics

from eventtracking import tracker
from ..accounts import NAME_MIN_LENGTH
from ..accounts.api import get_account_settings
from ..models import UserOrgTag
from ..helpers import intercept_errors

log = logging.getLogger(__name__)


class ProfileRequestError(Exception):
    """ The request to the API was not valid. """
    pass


class ProfileUserNotFound(ProfileRequestError):
    """ The requested user does not exist. """
    pass


class ProfileInternalError(Exception):
    """ An error occurred in an API call. """
    pass


FULL_NAME_MAX_LENGTH = 255
FULL_NAME_MIN_LENGTH = NAME_MIN_LENGTH


@intercept_errors(ProfileInternalError, ignore_errors=[ProfileRequestError])
def update_email_opt_in(user, org, optin):
    """Updates a user's preference for receiving org-wide emails.

    Sets a User Org Tag defining the choice to opt in or opt out of organization-wide
    emails.

    Arguments:
        user (User): The user to set a preference for.
        org (str): The org is used to determine the organization this setting is related to.
        optin (Boolean): True if the user is choosing to receive emails for this organization. If the user is not
            the correct age to receive emails, email-optin is set to False regardless.

    Returns:
        None

    """
    account_settings = get_account_settings(user)
    year_of_birth = account_settings['year_of_birth']
    of_age = (
        year_of_birth is None or  # If year of birth is not set, we assume user is of age.
        datetime.datetime.now(UTC).year - year_of_birth >  # pylint: disable=maybe-no-member
        getattr(settings, 'EMAIL_OPTIN_MINIMUM_AGE', 13)
    )

    try:
        preference, _ = UserOrgTag.objects.get_or_create(
            user=user, org=org, key='email-optin'
        )
        preference.value = str(optin and of_age)
        preference.save()

        if settings.FEATURES.get('SEGMENT_IO_LMS') and settings.SEGMENT_IO_LMS_KEY:
            _track_update_email_opt_in(user.id, org, optin)

    except IntegrityError as err:
        log.warn(u"Could not update organization wide preference due to IntegrityError: {}".format(err.message))


def _track_update_email_opt_in(user_id, organization, opt_in):
    """Track an email opt-in preference change.

    Arguments:
        user_id (str): The ID of the user making the preference change.
        organization (str): The organization whose emails are being opted into or out of by the user.
        opt_in (Boolean): Whether the user has chosen to opt-in to emails from the organization.

    Returns:
        None

    """
    event_name = 'edx.bi.user.org_email.opted_in' if opt_in else 'edx.bi.user.org_email.opted_out'
    tracking_context = tracker.get_tracker().resolve_context()

    analytics.track(
        user_id,
        event_name,
        {
            'category': 'communication',
            'label': organization
        },
        context={
            'Google Analytics': {
                'clientId': tracking_context.get('client_id')
            }
        }
    )
