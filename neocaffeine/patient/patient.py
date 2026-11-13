# One infant: covariates, append-only logs, validation flags, and ages derived from the clock.

from typing import Any

from neocaffeine.clock import ages
from neocaffeine.clock.time_axis import day_index
from neocaffeine.patient.append_only_log import AppendOnlyLog
from neocaffeine.patient.baseline_record import BaselineRecord
from neocaffeine.patient.blood_level_entry import BloodLevelEntry
from neocaffeine.patient.context_entry import ContextEntry
from neocaffeine.patient.covariates import Covariates
from neocaffeine.patient.detected_event import DetectedEvent
from neocaffeine.patient.dose_entry import DoseEntry
from neocaffeine.patient.daily_record import DailyRecord
from neocaffeine.patient.patient_errors import DefinitionalError, RecordingSequenceError
from neocaffeine.patient.range_validation import ValidationRanges
from neocaffeine.patient.signal_reference import SignalReference
from neocaffeine.patient.validation_flag import FlagKind, ValidationFlag
from neocaffeine.patient.weight_entry import WeightEntry

WEIGHT_LOG = "weight_log"
DOSE_LOG = "dose_log"
BLOOD_LEVEL_LOG = "blood_level_log"
CONTEXT_LOG = "context_log"
SIGNAL_REFERENCES = "signal_references"
DETECTED_EVENTS = "detected_events"
DAILY_RECORDS = "daily_records"
BASELINE_RECORDS = "baseline_records"
LOG_ENTRY_TYPES = {
    WEIGHT_LOG: WeightEntry,
    DOSE_LOG: DoseEntry,
    BLOOD_LEVEL_LOG: BloodLevelEntry,
    CONTEXT_LOG: ContextEntry,
    SIGNAL_REFERENCES: SignalReference,
    DETECTED_EVENTS: DetectedEvent,
    DAILY_RECORDS: DailyRecord,
    BASELINE_RECORDS: BaselineRecord,
}
OBSERVATION_LOGS = (BLOOD_LEVEL_LOG, DAILY_RECORDS)
DAILY_COUNT_RANGES = (
    ("apnea_count", "apnea_count"),
    ("bradycardia_count", "bradycardia_count"),
    ("desaturation_count", "desaturation_count"),
)


def build_logs() -> dict[str, AppendOnlyLog]:
    """Return one empty append-only log per log name, each with its time, duplicate and chronology rules."""
    return {
        WEIGHT_LOG: AppendOnlyLog(lambda entry: entry.time_hours, lambda entry: entry.time_hours),
        DOSE_LOG: AppendOnlyLog(lambda entry: entry.time_hours, lambda entry: entry.time_hours),
        BLOOD_LEVEL_LOG: AppendOnlyLog(lambda entry: entry.sampling_time_hours, lambda entry: entry.sampling_time_hours),
        CONTEXT_LOG: AppendOnlyLog(lambda entry: entry.time_hours, lambda entry: entry.time_hours),
        SIGNAL_REFERENCES: AppendOnlyLog(
            lambda entry: entry.start_hours,
            lambda entry: (entry.signal_type, entry.start_hours),
            lambda entry: entry.signal_type,
        ),
        DETECTED_EVENTS: AppendOnlyLog(
            lambda entry: entry.onset_hours,
            lambda entry: (entry.event_definition_version, entry.event_type, entry.onset_hours),
            lambda entry: (entry.event_definition_version, entry.event_type),
        ),
        DAILY_RECORDS: AppendOnlyLog(
            lambda entry: entry.day_index,
            lambda entry: (entry.event_definition_version, entry.day_index),
            lambda entry: entry.event_definition_version,
        ),
        BASELINE_RECORDS: AppendOnlyLog(
            lambda entry: 0.0,
            lambda entry: entry.event_definition_version,
            lambda entry: entry.event_definition_version,
        ),
    }


class Patient:
    """One infant, holding its covariates, its logs and the validation flags raised on them."""

    def __init__(self, covariates: Covariates, validation_ranges: ValidationRanges) -> None:
        """Create the patient and check its covariates against the validation ranges."""
        self._covariates = covariates
        self._validation_ranges = validation_ranges
        self._logs = build_logs()
        self._flags: list[ValidationFlag] = []
        self._last_recording_sequence = 0
        self._check_range(covariates.patient_id, "gestational_age", covariates.gestational_age_days, None)
        self._check_range(covariates.patient_id, "weight", covariates.birth_weight_grams, None)

    @property
    def covariates(self) -> Covariates:
        """Return the immutable covariates."""
        return self._covariates

    @property
    def patient_id(self) -> str:
        """Return the pseudonymous patient identifier."""
        return self._covariates.patient_id

    @property
    def last_recording_sequence(self) -> int:
        """Return the recording sequence number of the latest entry, or 0 if there is none."""
        return self._last_recording_sequence

    def _check_range(self, entry_id: str, range_name: str, value: float, day: int | None) -> None:
        """Store a flag if a value is outside its validation range, or if the range is empty."""
        check = self._validation_ranges.check(range_name, value)
        if not check.checked:
            self._flags.append(ValidationFlag(
                entry_id=entry_id,
                kind=FlagKind.RANGE_UNCHECKED,
                range_name=range_name,
                day_index=day,
                message=f"{range_name} not checked: the registry validation range is empty.",
            ))
        elif not check.inside:
            self._flags.append(ValidationFlag(
                entry_id=entry_id,
                kind=FlagKind.OUT_OF_VALIDATION_RANGE,
                range_name=range_name,
                day_index=day,
                message=f"{range_name} value {value} is outside the registry validation range.",
            ))

    def _range_checks(self, log_name: str, entry: Any) -> list[tuple[str, float, int | None]]:
        """Return the (range name, value, observation day) checks that apply to an entry of a log."""
        if log_name == WEIGHT_LOG:
            return [("weight", entry.weight_grams, day_index(entry.time_hours))]
        if log_name == DOSE_LOG:
            return [("dose_amount", entry.amount_mg_per_kg, day_index(entry.time_hours))]
        if log_name == BLOOD_LEVEL_LOG and entry.concentration_mg_per_l is not None:
            return [("blood_level", entry.concentration_mg_per_l, day_index(entry.sampling_time_hours))]
        if log_name == CONTEXT_LOG:
            return [("fio2", entry.fio2_fraction, day_index(entry.time_hours))]
        if log_name == DAILY_RECORDS:
            return [(range_name, getattr(entry, field), entry.day_index) for field, range_name in DAILY_COUNT_RANGES]
        return []

    def _record(self, log_name: str, entry: Any, recording_sequence: int) -> list[ValidationFlag]:
        """Append an entry to a log under a recording sequence number and return the flags it raised."""
        expected_type = LOG_ENTRY_TYPES[log_name]
        if not isinstance(entry, expected_type):
            raise DefinitionalError(f"{log_name} accepts {expected_type.__name__}, got {type(entry).__name__}.")
        if recording_sequence <= self._last_recording_sequence:
            raise RecordingSequenceError(
                f"Recording sequence {recording_sequence} is not after {self._last_recording_sequence}."
            )
        self._logs[log_name].append(entry, recording_sequence)
        self._last_recording_sequence = recording_sequence
        flag_count = len(self._flags)
        for range_name, value, day in self._range_checks(log_name, entry):
            self._check_range(entry.entry_id, range_name, value, day)
        return self._flags[flag_count:]

    def _add(self, log_name: str, entry: Any) -> list[ValidationFlag]:
        """Append an entry under the next recording sequence number."""
        return self._record(log_name, entry, self._last_recording_sequence + 1)

    def replay(self, log_name: str, entry: Any, recording_sequence: int) -> list[ValidationFlag]:
        """Restore a saved entry under its saved recording sequence; used when loading a patient file."""
        return self._record(log_name, entry, recording_sequence)

    def add_weight(self, entry: WeightEntry) -> list[ValidationFlag]:
        """Add a weight measurement and return its flags."""
        return self._add(WEIGHT_LOG, entry)

    def add_dose(self, entry: DoseEntry) -> list[ValidationFlag]:
        """Add a dose and return its flags."""
        return self._add(DOSE_LOG, entry)

    def add_blood_level(self, entry: BloodLevelEntry) -> list[ValidationFlag]:
        """Add a blood caffeine level and return its flags."""
        return self._add(BLOOD_LEVEL_LOG, entry)

    def add_context(self, entry: ContextEntry) -> list[ValidationFlag]:
        """Add a change of FiO2 or support mode and return its flags."""
        return self._add(CONTEXT_LOG, entry)

    def add_signal_reference(self, entry: SignalReference) -> list[ValidationFlag]:
        """Add a reference to a raw signal file."""
        return self._add(SIGNAL_REFERENCES, entry)

    def add_detected_event(self, entry: DetectedEvent) -> list[ValidationFlag]:
        """Add an event detected by the features layer."""
        return self._add(DETECTED_EVENTS, entry)

    def add_daily_record(self, entry: DailyRecord) -> list[ValidationFlag]:
        """Add a daily record and return its flags."""
        return self._add(DAILY_RECORDS, entry)

    def add_baseline_record(self, entry: BaselineRecord) -> list[ValidationFlag]:
        """Add the pre-dose baseline record of one event-definition version."""
        return self._add(BASELINE_RECORDS, entry)

    def log(self, log_name: str) -> AppendOnlyLog:
        """Return one of the patient's logs by name."""
        return self._logs[log_name]

    def weights(self) -> tuple[WeightEntry, ...]:
        """Return the current weight measurements in time order."""
        return self._logs[WEIGHT_LOG].current_entries()

    def doses(self) -> tuple[DoseEntry, ...]:
        """Return the current doses in time order."""
        return self._logs[DOSE_LOG].current_entries()

    def blood_levels(self) -> tuple[BloodLevelEntry, ...]:
        """Return the current blood levels in time order."""
        return self._logs[BLOOD_LEVEL_LOG].current_entries()

    def context_changes(self) -> tuple[ContextEntry, ...]:
        """Return the current context changes in time order."""
        return self._logs[CONTEXT_LOG].current_entries()

    def signal_references(self) -> tuple[SignalReference, ...]:
        """Return the current raw-signal references in time order."""
        return self._logs[SIGNAL_REFERENCES].current_entries()

    def detected_events(self, event_definition_version: float) -> tuple[DetectedEvent, ...]:
        """Return the current events detected under one event-definition version."""
        return tuple(
            event for event in self._logs[DETECTED_EVENTS].current_entries()
            if event.event_definition_version == event_definition_version
        )

    def daily_records(self, event_definition_version: float) -> tuple[DailyRecord, ...]:
        """Return the current daily records of one event-definition version, in day order."""
        return tuple(
            record for record in self._logs[DAILY_RECORDS].current_entries()
            if record.event_definition_version == event_definition_version
        )

    def baseline_record(self, event_definition_version: float) -> BaselineRecord | None:
        """Return the current baseline record of one event-definition version, or None."""
        for record in self._logs[BASELINE_RECORDS].current_entries():
            if record.event_definition_version == event_definition_version:
                return record
        return None

    def has_baseline_window(self, event_definition_version: float) -> bool:
        """Return False when there is no baseline record, so outputs carry no_baseline_window."""
        return self.baseline_record(event_definition_version) is not None

    def weight_grams_at(self, hours: float) -> float:
        """Return the latest weight measured at or before the time, or the birth weight before the first one."""
        measured = [entry for entry in self.weights() if entry.time_hours <= hours]
        return measured[-1].weight_grams if measured else self._covariates.birth_weight_grams

    def day_of_life(self, hours: float) -> int:
        """Return the day of life, counting the first day as day 1."""
        return ages.day_of_life(hours)

    def postnatal_age_days(self, hours: float) -> float:
        """Return the continuous postnatal age in days."""
        return ages.postnatal_age_days(hours)

    def postmenstrual_age_days(self, hours: float) -> float:
        """Return the postmenstrual age in days."""
        return ages.postmenstrual_age_days(self._covariates.gestational_age_days, hours)

    def postmenstrual_age_weeks(self, hours: float) -> float:
        """Return the postmenstrual age in weeks."""
        return ages.postmenstrual_age_weeks(self._covariates.gestational_age_days, hours)

    def validation_flags(self) -> tuple[ValidationFlag, ...]:
        """Return every flag raised, for covariates and for every entry ever added."""
        return tuple(self._flags)

    def current_entry_ids(self, log_name: str) -> frozenset[str]:
        """Return the identifiers of the current entries of a log."""
        return frozenset(entry.entry_id for entry in self._logs[log_name].current_entries())

    def excluded_days(self) -> frozenset[int]:
        """Return the observation days excluded from estimation because a current observation is out of range."""
        current_observation_ids = frozenset().union(*(self.current_entry_ids(name) for name in OBSERVATION_LOGS))
        return frozenset(
            flag.day_index
            for flag in self._flags
            if flag.kind == FlagKind.OUT_OF_VALIDATION_RANGE and flag.entry_id in current_observation_ids
        )

    def entry_flags(self, entry_id: str) -> tuple[ValidationFlag, ...]:
        """Return the flags of one entry or of the covariates (by patient identifier)."""
        return tuple(flag for flag in self._flags if flag.entry_id == entry_id)

    def recording_order(self) -> list[tuple[int, str, Any]]:
        """Return every entry of every log as (recording sequence, log name, entry), in recording order."""
        rows = [
            (recorded.recording_sequence, log_name, recorded.entry)
            for log_name, log in self._logs.items()
            for recorded in log.recorded_entries()
        ]
        return sorted(rows, key=lambda row: row[0])
