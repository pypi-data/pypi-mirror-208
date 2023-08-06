from typing import Dict
from dataclasses import dataclass, field

from anastasia_logging.codes.standard_errors import _STANDARD_ERROR_CODES
from anastasia_logging.codes.standard_warning import _STANDARD_WARNING_CODES
from anastasia_logging.codes.standard_info import _STANDARD_INFO_CODES

@dataclass
class StandardCodes:
    """

    Standard Codifications

    Base codes are the following ones:

    -   0 = Unindentified
    - 1XX = Data related
    - 2XX = Mathematical related
    - 3XX = AI related
    - 4XX = Resources related
    - 5XX = Operative System (OS) related
    - 6XX = API related
    - 7XX = AWS related

    """

    ERROR: Dict[int, str] = field(default_factory=lambda: _STANDARD_ERROR_CODES)
    WARNING: Dict[int, str] = field(default_factory=lambda: _STANDARD_WARNING_CODES)
    INFO: Dict[int, str] = field(default_factory=lambda: _STANDARD_INFO_CODES)