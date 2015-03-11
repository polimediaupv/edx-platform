"""Python API for user accounts.


Account information includes a student's username, password, and email
address, but does NOT include user profile information (i.e., demographic
information and preferences).

"""
from django.conf import settings
from django.db import transaction, IntegrityError
from django.core.validators import validate_email, validate_slug, ValidationError

from ..forms import PasswordResetFormNoActive
from ..models import User, UserProfile, Registration
from ..helpers import intercept_errors

from .user import UserApiRequestError, UserApiInternalError, UserNotFound, UserNotAuthorized


USERNAME_MIN_LENGTH = 2
USERNAME_MAX_LENGTH = 30

EMAIL_MIN_LENGTH = 3
EMAIL_MAX_LENGTH = 254

PASSWORD_MIN_LENGTH = 2
PASSWORD_MAX_LENGTH = 75


class AccountRequestError(UserApiRequestError):
    """There was a problem with the request to the account API. """
    pass


class AccountInternalError(Exception):
    """An internal error occurred in the account API. """
    pass


class AccountUserAlreadyExists(AccountRequestError):
    """User with the same username and/or email already exists. """
    pass


class AccountUsernameInvalid(AccountRequestError):
    """The requested username is not in a valid format. """
    pass


class AccountEmailInvalid(AccountRequestError):
    """The requested email is not in a valid format. """
    pass


class AccountPasswordInvalid(AccountRequestError):
    """The requested password is not in a valid format. """
    pass


class AccountUpdateError(AccountRequestError):
    """
    An update to the account failed. More detailed information is present in developer_message,
    and depending on the type of error encountered, there may also be a non-null user_message field.
    """
    def __init__(self, developer_message, user_message=None):
        self.developer_message = developer_message
        self.user_message = user_message


class AccountValidationError(AccountRequestError):
    """
    Validation issues were found with the supplied data. More detailed information is present in field_errors,
    a dict with specific information about each field that failed validation. For each field,
    there will be at least a developer_message describing the validation issue, and possibly
    also a user_message.
    """
    def __init__(self, field_errors):
        self.field_errors = field_errors


@intercept_errors(UserApiInternalError, ignore_errors=[UserApiRequestError])
@transaction.commit_on_success
def create_account(username, password, email):
    """Create a new user account.

    This will implicitly create an empty profile for the user.

    WARNING: This function does NOT yet implement all the features
    in `student/views.py`.  Until it does, please use this method
    ONLY for tests of the account API, not in production code.
    In particular, these are currently missing:

    * 3rd party auth
    * External auth (shibboleth)
    * Complex password policies (ENFORCE_PASSWORD_POLICY)

    In addition, we assume that some functionality is handled
    at higher layers:

    * Analytics events
    * Activation email
    * Terms of service / honor code checking
    * Recording demographic info (use profile API)
    * Auto-enrollment in courses (if invited via instructor dash)

    Args:
        username (unicode): The username for the new account.
        password (unicode): The user's password.
        email (unicode): The email address associated with the account.

    Returns:
        unicode: an activation key for the account.

    Raises:
        AccountUserAlreadyExists
        AccountUsernameInvalid
        AccountEmailInvalid
        AccountPasswordInvalid

    """
    # Validate the username, password, and email
    # This will raise an exception if any of these are not in a valid format.
    _validate_username(username)
    _validate_password(password, username)
    _validate_email(email)

    # Create the user account, setting them to "inactive" until they activate their account.
    user = User(username=username, email=email, is_active=False)
    user.set_password(password)

    try:
        user.save()
    except IntegrityError:
        raise AccountUserAlreadyExists

    # Create a registration to track the activation process
    # This implicitly saves the registration.
    registration = Registration()
    registration.register(user)

    # Create an empty user profile with default values
    UserProfile(user=user).save()

    # Return the activation key, which the caller should send to the user
    return registration.activation_key


def check_account_exists(username=None, email=None):
    """Check whether an account with a particular username or email already exists.

    Keyword Arguments:
        username (unicode)
        email (unicode)

    Returns:
        list of conflicting fields

    Example Usage:
        >>> account_api.check_account_exists(username="bob")
        []
        >>> account_api.check_account_exists(username="ted", email="ted@example.com")
        ["email", "username"]

    """
    conflicts = []

    if email is not None and User.objects.filter(email=email).exists():
        conflicts.append("email")

    if username is not None and User.objects.filter(username=username).exists():
        conflicts.append("username")

    return conflicts


@intercept_errors(UserApiInternalError, ignore_errors=[UserApiRequestError])
def account_info(username):
    """Retrieve information about a user's account.

    Arguments:
        username (unicode): The username associated with the account.

    Returns:
        dict: User's account information, if the user was found.
        None: The user does not exist.

    """
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return None
    else:
        return {
            u'username': username,
            u'email': user.email,
            u'is_active': user.is_active,
        }


@intercept_errors(UserApiInternalError, ignore_errors=[UserApiRequestError])
def activate_account(activation_key):
    """Activate a user's account.

    Args:
        activation_key (unicode): The activation key the user received via email.

    Returns:
        None

    Raises:
        UserNotAuthorized

    """
    try:
        registration = Registration.objects.get(activation_key=activation_key)
    except Registration.DoesNotExist:
        raise UserNotAuthorized
    else:
        # This implicitly saves the registration
        registration.activate()


@intercept_errors(UserApiInternalError, ignore_errors=[UserApiRequestError])
def request_password_change(email, orig_host, is_secure):
    """Email a single-use link for performing a password reset.

    Users must confirm the password change before we update their information.

    Args:
        email (string): An email address
        orig_host (string): An originating host, extracted from a request with get_host
        is_secure (Boolean): Whether the request was made with HTTPS

    Returns:
        None

    Raises:
        AccountUserNotFound
        AccountRequestError

    """
    # Binding data to a form requires that the data be passed as a dictionary
    # to the Form class constructor.
    form = PasswordResetFormNoActive({'email': email})

    # Validate that a user exists with the given email address.
    if form.is_valid():
        # Generate a single-use link for performing a password reset
        # and email it to the user.
        form.save(
            from_email=settings.DEFAULT_FROM_EMAIL,
            domain_override=orig_host,
            use_https=is_secure
        )
    else:
        # No user with the provided email address exists.
        raise UserNotFound


def _validate_username(username):
    """Validate the username.

    Arguments:
        username (unicode): The proposed username.

    Returns:
        None

    Raises:
        AccountUsernameInvalid

    """
    if not isinstance(username, basestring):
        raise AccountUsernameInvalid(u"Username must be a string")

    if len(username) < USERNAME_MIN_LENGTH:
        raise AccountUsernameInvalid(
            u"Username '{username}' must be at least {min} characters long".format(
                username=username,
                min=USERNAME_MIN_LENGTH
            )
        )
    if len(username) > USERNAME_MAX_LENGTH:
        raise AccountUsernameInvalid(
            u"Username '{username}' must be at most {max} characters long".format(
                username=username,
                max=USERNAME_MAX_LENGTH
            )
        )
    try:
        validate_slug(username)
    except ValidationError:
        raise AccountUsernameInvalid(
            u"Username '{username}' must contain only A-Z, a-z, 0-9, -, or _ characters"
        )


def _validate_password(password, username):
    """Validate the format of the user's password.

    Passwords cannot be the same as the username of the account,
    so we take `username` as an argument.

    Arguments:
        password (unicode): The proposed password.
        username (unicode): The username associated with the user's account.

    Returns:
        None

    Raises:
        AccountPasswordInvalid

    """
    if not isinstance(password, basestring):
        raise AccountPasswordInvalid(u"Password must be a string")

    if len(password) < PASSWORD_MIN_LENGTH:
        raise AccountPasswordInvalid(
            u"Password must be at least {min} characters long".format(
                min=PASSWORD_MIN_LENGTH
            )
        )

    if len(password) > PASSWORD_MAX_LENGTH:
        raise AccountPasswordInvalid(
            u"Password must be at most {max} characters long".format(
                max=PASSWORD_MAX_LENGTH
            )
        )

    if password == username:
        raise AccountPasswordInvalid(u"Password cannot be the same as the username")


def _validate_email(email):
    """Validate the format of the email address.

    Arguments:
        email (unicode): The proposed email.

    Returns:
        None

    Raises:
        AccountEmailInvalid

    """
    if not isinstance(email, basestring):
        raise AccountEmailInvalid(u"Email must be a string")

    if len(email) < EMAIL_MIN_LENGTH:
        raise AccountEmailInvalid(
            u"Email '{email}' must be at least {min} characters long".format(
                email=email,
                min=EMAIL_MIN_LENGTH
            )
        )

    if len(email) > EMAIL_MAX_LENGTH:
        raise AccountEmailInvalid(
            u"Email '{email}' must be at most {max} characters long".format(
                email=email,
                max=EMAIL_MAX_LENGTH
            )
        )

    try:
        validate_email(email)
    except ValidationError:
        raise AccountEmailInvalid(
            u"Email '{email}' format is not valid".format(email=email)
        )
