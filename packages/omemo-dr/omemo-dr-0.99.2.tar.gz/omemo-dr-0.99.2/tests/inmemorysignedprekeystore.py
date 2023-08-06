from __future__ import annotations

from omemo_dr.exceptions import InvalidKeyIdException
from omemo_dr.state.signedprekeyrecord import SignedPreKeyRecord


class InMemorySignedPreKeyStore:
    def __init__(self):
        self.store: dict[int, bytes] = {}

    def load_signed_pre_key(self, signed_pre_key_id: int) -> SignedPreKeyRecord:
        if signed_pre_key_id not in self.store:
            raise InvalidKeyIdException(
                "No such signedprekeyrecord! %s " % signed_pre_key_id
            )

        return SignedPreKeyRecord.from_bytes(self.store[signed_pre_key_id])

    def load_signed_pre_keys(self) -> list[SignedPreKeyRecord]:
        results: list[SignedPreKeyRecord] = []
        for serialized in self.store.values():
            results.append(SignedPreKeyRecord.from_bytes(serialized))

        return results

    def store_signed_pre_key(
        self, signed_pre_key_id: int, signed_pre_key_record: SignedPreKeyRecord
    ) -> None:
        self.store[signed_pre_key_id] = signed_pre_key_record.serialize()

    def contains_signed_pre_key(self, signed_pre_key_id: int) -> bool:
        return signed_pre_key_id in self.store

    def remove_signed_pre_key(self, signed_pre_key_id: int) -> None:
        del self.store[signed_pre_key_id]
