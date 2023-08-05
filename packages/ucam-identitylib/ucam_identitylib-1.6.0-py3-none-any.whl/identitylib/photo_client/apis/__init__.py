
# flake8: noqa

# Import all APIs into this package.
# If you have many APIs here with many many models used in each API this may
# raise a `RecursionError`.
# In order to avoid this, import only the API that you directly need like:
#
#   from identitylib.photo_client.api.api_versions_api import APIVersionsApi
#
# or import this package, but before doing it, use:
#
#   import sys
#   sys.setrecursionlimit(n)

# Import APIs into API package:
from identitylib.photo_client.api.api_versions_api import APIVersionsApi
from identitylib.photo_client.api.all_photos_api import AllPhotosApi
from identitylib.photo_client.api.approved_photos_api import ApprovedPhotosApi
from identitylib.photo_client.api.permissions_api import PermissionsApi
from identitylib.photo_client.api.photo_identifier_api import PhotoIdentifierApi
from identitylib.photo_client.api.photo_identifiers_api import PhotoIdentifiersApi
from identitylib.photo_client.api.photo_identifiers_including_photos_api import PhotoIdentifiersIncludingPhotosApi
from identitylib.photo_client.api.photos_including_unapproved_photos_api import PhotosIncludingUnapprovedPhotosApi
from identitylib.photo_client.api.unapproved_photos_api import UnapprovedPhotosApi
