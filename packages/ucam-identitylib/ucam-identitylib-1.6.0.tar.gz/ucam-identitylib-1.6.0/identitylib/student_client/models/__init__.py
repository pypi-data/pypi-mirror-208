# flake8: noqa

# import all models into this package
# if you have many models here with many references from one model to another this may
# raise a RecursionError
# to avoid this, import only the models that you directly need like:
# from identitylib.student_client.model.pet import Pet
# or import this package, but before doing it, use:
# import sys
# sys.setrecursionlimit(n)

from identitylib.student_client.model.affiliation import Affiliation
from identitylib.student_client.model.affiliation_scheme import AffiliationScheme
from identitylib.student_client.model.http_exception import HTTPException
from identitylib.student_client.model.http_validation_error import HTTPValidationError
from identitylib.student_client.model.identifier import Identifier
from identitylib.student_client.model.identifier_scheme import IdentifierScheme
from identitylib.student_client.model.location_inner import LocationInner
from identitylib.student_client.model.paginated_results_student import PaginatedResultsStudent
from identitylib.student_client.model.student import Student
from identitylib.student_client.model.validation_error import ValidationError
