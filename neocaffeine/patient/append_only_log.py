# An append-only log: chronology of original entries, duplicate checks, corrections and the current view.

from collections.abc import Callable, Hashable
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from neocaffeine.patient.patient_errors import (
    AlreadySupersededError,
    ChronologyError,
    DuplicateEntryIdError,
    DuplicateTimeError,
    UnknownEntryError,
)

EntryType = TypeVar("EntryType")


def single_group(entry: Any) -> Hashable:
    """Return the same chronology group for every entry."""
    return None


@dataclass(frozen=True)
class RecordedEntry(Generic[EntryType]):
    """An entry together with the recording sequence number it was added under."""

    entry: EntryType
    recording_sequence: int


class AppendOnlyLog(Generic[EntryType]):
    """Entries are only ever added; corrections supersede earlier entries without changing them."""

    def __init__(
        self,
        event_time: Callable[[EntryType], float],
        duplicate_key: Callable[[EntryType], Hashable],
        chronology_group: Callable[[EntryType], Hashable] = single_group,
    ) -> None:
        """Create an empty log ordered by event_time, with duplicates detected by duplicate_key."""
        self._event_time = event_time
        self._duplicate_key = duplicate_key
        self._chronology_group = chronology_group
        self._recorded: list[RecordedEntry[EntryType]] = []
        self._superseded_by: dict[str, str] = {}

    def _entry_ids(self) -> set[str]:
        """Return the identifiers of every entry in the log."""
        return {recorded.entry.entry_id for recorded in self._recorded}

    def _require_valid_correction(self, entry: EntryType) -> None:
        """Raise unless the entry supersedes an existing entry that nothing supersedes yet."""
        superseded_id = entry.correction.supersedes
        if superseded_id not in self._entry_ids():
            raise UnknownEntryError(f"Entry {entry.entry_id} supersedes unknown entry {superseded_id}.")
        if superseded_id in self._superseded_by:
            raise AlreadySupersededError(
                f"Entry {superseded_id} is already superseded by {self._superseded_by[superseded_id]}."
            )

    def _require_chronological(self, entry: EntryType) -> None:
        """Raise if an original entry is earlier than the latest original entry of its group."""
        group = self._chronology_group(entry)
        earlier_times = [
            self._event_time(recorded.entry)
            for recorded in self._recorded
            if recorded.entry.correction is None and self._chronology_group(recorded.entry) == group
        ]
        if earlier_times and self._event_time(entry) < max(earlier_times):
            raise ChronologyError(
                f"Entry at {self._event_time(entry)} is earlier than the latest entry at {max(earlier_times)}."
            )

    def _require_no_duplicate(self, entry: EntryType) -> None:
        """Raise if the entry repeats the key of a current entry, other than the one it replaces."""
        replaced_id = None if entry.correction is None else entry.correction.supersedes
        key = self._duplicate_key(entry)
        for current in self.current_entries():
            if current.entry_id != replaced_id and self._duplicate_key(current) == key:
                raise DuplicateTimeError(f"Entry {entry.entry_id} repeats {key!r} of entry {current.entry_id}.")

    def append(self, entry: EntryType, recording_sequence: int) -> None:
        """Add an original entry or a correction under the given recording sequence number."""
        if entry.entry_id in self._entry_ids():
            raise DuplicateEntryIdError(f"Entry identifier {entry.entry_id} is already used.")
        if entry.correction is None:
            self._require_chronological(entry)
        else:
            self._require_valid_correction(entry)
        self._require_no_duplicate(entry)
        self._recorded.append(RecordedEntry(entry=entry, recording_sequence=recording_sequence))
        if entry.correction is not None:
            self._superseded_by[entry.correction.supersedes] = entry.entry_id

    def recorded_entries(self) -> tuple[RecordedEntry[EntryType], ...]:
        """Return every entry ever added, superseded ones included, in recording order."""
        return tuple(self._recorded)

    def all_entries(self) -> tuple[EntryType, ...]:
        """Return every entry ever added, superseded ones included, in recording order."""
        return tuple(recorded.entry for recorded in self._recorded)

    def current_entries(self) -> tuple[EntryType, ...]:
        """Return the entries no correction supersedes, ordered by event time, then recording order."""
        current = [recorded for recorded in self._recorded if recorded.entry.entry_id not in self._superseded_by]
        current.sort(key=lambda recorded: (self._event_time(recorded.entry), recorded.recording_sequence))
        return tuple(recorded.entry for recorded in current)
