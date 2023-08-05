
# flake8: noqa

# Import all APIs into this package.
# If you have many APIs here with many many models used in each API this may
# raise a `RecursionError`.
# In order to avoid this, import only the API that you directly need like:
#
#   from identitylib.lookup_client.api.group_api import GroupApi
#
# or import this package, but before doing it, use:
#
#   import sys
#   sys.setrecursionlimit(n)

# Import APIs into API package:
from identitylib.lookup_client.api.group_api import GroupApi
from identitylib.lookup_client.api.ibis_api import IbisApi
from identitylib.lookup_client.api.institution_api import InstitutionApi
from identitylib.lookup_client.api.person_api import PersonApi
