# Purpose: Canonical enum values and payload keys for API contract consistency; scientific vocabularies follow neocaffeine.patient.vocabularies.

from neocaffeine.patient.vocabularies import Route, SaltForm, Sex, SupportMode

PHASE_PLAYING = "playing"
PHASE_AWAITING_N = "awaiting_n"
PHASE_CONVERGED = "converged"
PHASE_UPDATING_CLIENT_ONLY = "updating"

EVENT_APNEA = "apnea"
EVENT_BRADYCARDIA = "bradycardia"
EVENT_DESATURATION = "desaturation"

SEX_VALUES = frozenset(str(value) for value in Sex)
ROUTE_VALUES = frozenset(str(value) for value in Route)
FORM_VALUES = frozenset(str(value) for value in SaltForm)
BREATHING_SUPPORT_VALUES = frozenset(str(value) for value in SupportMode)

DOSE_UNIT_MG_PER_KG = "mg_per_kg"
DOSE_UNIT_MG = "mg"
