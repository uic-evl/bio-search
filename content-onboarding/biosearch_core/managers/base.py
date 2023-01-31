""" Enums and constants for managing the project structure"""

from enum import Enum


class Structure(Enum):
    """Folders inside the project to organize folder content"""

    INDEXES = "indexes"
    DATA = "data"
    TO_PREDICT = "to_predict"
    TO_IMPORT = "to_import"
    TO_SEGMENT = "to_segment"
    TO_EXTRACT = "to_extract"
    ERRORS = "errors"
    NO_METADATA = "not_in_metadata"
    MULTIPLE_PDFS = "multiple_pdfs"
    NO_PDFS = "missing_pdf"
    XPDF = "xpdf"
    LOGS = "logs"
