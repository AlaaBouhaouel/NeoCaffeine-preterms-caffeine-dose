# Named exceptions raised by the patient package.


class PatientError(ValueError):
    """Base class for every error raised by the patient package."""


class DefinitionalError(PatientError):
    """Raised when a value is impossible by definition, such as a negative weight."""


class MissingCovariateError(PatientError):
    """Raised when a required covariate is empty."""


class ChronologyError(PatientError):
    """Raised when an original entry is earlier than the latest original entry of its log."""


class DuplicateTimeError(PatientError):
    """Raised when an entry repeats the time of a current entry of the same log type."""


class UnknownEntryError(PatientError):
    """Raised when a correction supersedes an entry that does not exist in its log."""


class AlreadySupersededError(PatientError):
    """Raised when a correction supersedes an entry that another entry already supersedes."""


class DuplicateEntryIdError(PatientError):
    """Raised when an entry reuses the identifier of an existing entry."""


class RecordingSequenceError(PatientError):
    """Raised when a restored recording sequence number is not strictly increasing."""


class PatientFileError(PatientError):
    """Raised when a patient file cannot be read or does not follow the patient format."""


class UnsupportedSchemaVersionError(PatientFileError):
    """Raised when a patient file has a schema version this code does not read."""
