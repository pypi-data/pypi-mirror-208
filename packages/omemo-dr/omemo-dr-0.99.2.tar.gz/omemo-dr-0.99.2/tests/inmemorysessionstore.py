from __future__ import annotations

from omemo_dr.state.sessionrecord import SessionRecord


class InMemorySessionStore:
    def __init__(self):
        self.sessions: dict[tuple[str, int], bytes] = {}

    def load_session(self, recipient_id: str, device_id: int) -> SessionRecord:
        if self.contains_session(recipient_id, device_id):
            return SessionRecord(serialized=self.sessions[(recipient_id, device_id)])
        else:
            return SessionRecord()

    def store_session(
        self, recipient_id: str, device_id: int, session_record: SessionRecord
    ) -> None:
        self.sessions[(recipient_id, device_id)] = session_record.serialize()

    def contains_session(self, recipient_id: str, device_id: int) -> bool:
        return (recipient_id, device_id) in self.sessions

    def delete_session(self, recipient_id: str, device_id: int) -> None:
        del self.sessions[(recipient_id, device_id)]

    def delete_all_sessions(self, recipient_id: str) -> None:
        for k in self.sessions.keys():
            if k[0] == recipient_id:
                del self.sessions[k]
