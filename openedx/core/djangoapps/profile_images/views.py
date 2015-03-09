from contextlib import closing
import hashlib

from django.conf import settings
from django.core.files.storage import get_storage_class
from django.core.files.images import ImageFile

from rest_framework import permissions, status
from rest_framework.authentication import OAuth2Authentication, SessionAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView


# TODO: move these to settings
PROFILE_IMAGE_STORAGE_CLASS = 'django.core.files.storage.FileSystemStorage'
PROFILE_IMAGE_MAX_BYTES = 2.5 * 1024 * 1024 * 1024  # TODO arbitrary
PROFILE_IMAGE_MAX_DIMENSIONS = '1280x1280'  # TODO arbitrary


class InvalidProfileImage(Exception):
    """
    Local Exception type that helps us clean up after file validation
    failures, and communicate what went wrong to the user.
    """
    pass


def validate_profile_image(image_file, content_type):
    """
    Raises an InvalidProfileImage if the server should refuse to store this
    uploaded file as a user's profile image.

    Otherwise, returns a cleaned version of the extension as a string, i.e. one
    of: ('gif', 'jpeg', 'png')
    """
    image_types = {
        'jpeg' : {
            'extension': [".jpeg", ".jpg"],
            'mimetypes': ['image/jpeg', 'image/pjpeg'],
            'magic': ["ffd8"]
            },
        'png': {
            'extension': [".png"],
            'mimetypes': ['image/png'],
            'magic': ["89504e470d0a1a0a"]
            },
        'gif': {
            'extension': [".gif"],
            'mimetypes': ['image/gif'],
            'magic': ["474946383961", "474946383761"]
            }
        }

    # check file size
    if image_file.size > PROFILE_IMAGE_MAX_BYTES:
        raise InvalidProfileImage("file size limit exceeded")
    elif image_file.size < 4:
        raise InvalidProfileImage("file too small")  # TODO arbitrary

    # check the file extension looks acceptable
    filename = str(image_file.name).lower()
    filetype = [ft for ft in image_types if any(filename.endswith(ext) for ext in image_types[ft]['extension'])]
    if not filetype:
        return InvalidProfileImage("unsupported file extension")
    filetype = filetype[0]

    # check mimetype matches expected file type
    if content_type not in image_types[filetype]['mimetypes']:
        raise InvalidProfileImage("Mismatch between file type and mimetype")

    # check image file headers match expected file type
    # TODO: better to use PIL for this?  dimension check for free there.
    headers = image_types[filetype]['magic']
    if image_file.read(len(headers[0])/2).encode('hex') not in headers:
        raise InvalidProfileImage("Mismatch between file type and header")
    # avoid unexpected errors from subsequent modules expecting the fp to be at 0
    image_file.seek(0)
    return filetype


def store_profile_image(image_file, username, extension):
    """
    Permanently store the contents of the uploaded_file as this user's profile
    image, in whatever storage backend we're configured to use.  Any
    previously-stored profile image will be overwritten.

    Returns the path to the stored file.
    """
    storage = get_storage_class(PROFILE_IMAGE_STORAGE_CLASS)()
    dest_name = storage.get_valid_name('{}_profile_orig.{}'.format(hashlib.md5(username).hexdigest(), extension))
    if storage.exists(dest_name):
        storage.delete(dest_name)
    path = storage.save(dest_name, image_file)
    return path


class ProfileImageUploadView(APIView):

    parser_classes = (MultiPartParser, FormParser,)

    authentication_classes = (OAuth2Authentication, SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, username):

        # request validation.

        # ensure authenticated user is either same as username, or is staff.
        # TODO

        # ensure file exists at all!
        if 'file' not in request.FILES:
            raise Exception("no file enclosed")  # 400

        uploaded_file = request.FILES['file']

        # no matter what happens, delete the temporary file when we're done
        with closing(uploaded_file):

            # image file validation.
            try:
                file_type = validate_profile_image(uploaded_file, uploaded_file.content_type)
            except InvalidProfileImage, e:
                return Response(
                    {
                        "developer_message": e.message,
                        "user_message": None
                    },
                    status = status.HTTP_400_BAD_REQUEST
                )

            # Store the validated file.
            stored_path = store_profile_image(uploaded_file, username, file_type)

            # update the user account to reflect that a profile image is available.
            # TODO

        # send user response.
        return Response({"path": stored_path})