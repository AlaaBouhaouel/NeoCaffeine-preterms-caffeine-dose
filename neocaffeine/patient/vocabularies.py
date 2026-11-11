# Fixed vocabularies of the patient object, as lowercase snake_case enums.

from enum import StrEnum


class Sex(StrEnum):
    """Sex of the infant."""

    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"


class Route(StrEnum):
    """Route of a caffeine dose; intravenous only in this version."""

    IV = "iv"


class SaltForm(StrEnum):
    """Whether a dose amount is caffeine citrate or caffeine base."""

    CITRATE = "citrate"
    BASE = "base"


class SampleType(StrEnum):
    """Type of blood sample a caffeine level was measured in."""

    SERUM = "serum"
    PLASMA = "plasma"
    DRIED_BLOOD_SPOT = "dried_blood_spot"


class SupportMode(StrEnum):
    """Breathing support mode."""

    ROOM_AIR = "room_air"
    LOW_FLOW = "low_flow"
    HFNC = "hfnc"
    CPAP = "cpap"
    NIPPV = "nippv"
    INVASIVE_VENTILATION = "invasive_ventilation"


class SignalType(StrEnum):
    """Type of a raw signal referenced by the patient."""

    SPO2 = "spo2"
    HEART_RATE = "heart_rate"
    RESPIRATION = "respiration"
    EEG = "eeg"


class EventType(StrEnum):
    """Type of a detected event."""

    APNEA = "apnea"
    BRADYCARDIA = "bradycardia"
    DESATURATION = "desaturation"
