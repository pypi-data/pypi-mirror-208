# flake8: noqa

# import all models into this package
# if you have many models here with many references from one model to another this may
# raise a RecursionError
# to avoid this, import only the models that you directly need like:
# from identitylib.inst_identifier_client.model.pet import Pet
# or import this package, but before doing it, use:
# import sys
# sys.setrecursionlimit(n)

from identitylib.inst_identifier_client.model.mapping_datum import MappingDatum
from identitylib.inst_identifier_client.model.mapping_response import MappingResponse
