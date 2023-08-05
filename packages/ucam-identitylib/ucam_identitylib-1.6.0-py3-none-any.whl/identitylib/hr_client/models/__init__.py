# flake8: noqa

# import all models into this package
# if you have many models here with many references from one model to another this may
# raise a RecursionError
# to avoid this, import only the models that you directly need like:
# from identitylib.hr_client.model.pet import Pet
# or import this package, but before doing it, use:
# import sys
# sys.setrecursionlimit(n)

from identitylib.hr_client.model.affiliation import Affiliation
from identitylib.hr_client.model.affiliation_scheme import AffiliationScheme
from identitylib.hr_client.model.http_exception import HTTPException
from identitylib.hr_client.model.http_validation_error import HTTPValidationError
from identitylib.hr_client.model.identifier import Identifier
from identitylib.hr_client.model.identifier_scheme import IdentifierScheme
from identitylib.hr_client.model.location_inner import LocationInner
from identitylib.hr_client.model.paginated_results_staff_member import PaginatedResultsStaffMember
from identitylib.hr_client.model.staff_member import StaffMember
from identitylib.hr_client.model.validation_error import ValidationError
