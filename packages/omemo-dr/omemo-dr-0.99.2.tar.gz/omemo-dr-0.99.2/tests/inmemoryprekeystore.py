from __future__ import annotations

from omemo_dr.exceptions import InvalidKeyIdException
from omemo_dr.state.prekeyrecord import PreKeyRecord


class InMemoryPreKeyStore:
    def __init__(self) -> None:
        self.store: dict[int, bytes] = {}

    def load_pre_key(self, pre_key_id: int) -> PreKeyRecord:
        if pre_key_id not in self.store:
            raise InvalidKeyIdException("No such prekeyRecord!")

        return PreKeyRecord.from_bytes(self.store[pre_key_id])

    def store_pre_key(self, pre_key_id: int, pre_key_record: PreKeyRecord) -> None:
        self.store[pre_key_id] = pre_key_record.serialize()

    def contains_pre_key(self, pre_key_id: int) -> bool:
        return pre_key_id in self.store

    def remove_pre_key(self, pre_key_id: int) -> None:
        if pre_key_id in self.store:
            del self.store[pre_key_id]
