from __future__ import annotations

from omemo_dr.identitykey import IdentityKey
from omemo_dr.identitykeypair import IdentityKeyPair
from omemo_dr.state.store import Store

from .inmemoryidentitykeystore import InMemoryIdentityKeyStore
from .inmemoryprekeystore import InMemoryPreKeyStore
from .inmemoryprekeystore import PreKeyRecord
from .inmemorysessionstore import InMemorySessionStore
from .inmemorysessionstore import SessionRecord
from .inmemorysignedprekeystore import InMemorySignedPreKeyStore
from .inmemorysignedprekeystore import SignedPreKeyRecord


class InMemoryStore(Store):
    def __init__(self):
        self.identity_key_store = InMemoryIdentityKeyStore()
        self.pre_key_store = InMemoryPreKeyStore()
        self.signed_pre_key_store = InMemorySignedPreKeyStore()
        self.session_store = InMemorySessionStore()

    def get_identity_key_pair(self) -> IdentityKeyPair:
        return self.identity_key_store.get_identity_key_pair()

    def get_our_device_id(self) -> int:
        return self.identity_key_store.get_our_device_id()

    def save_identity(self, recipient_id: str, identity_key: IdentityKey) -> None:
        self.identity_key_store.save_identity(recipient_id, identity_key)

    def is_trusted_identity(self, recipient_id: str, identity_key: IdentityKey) -> bool:
        return self.identity_key_store.is_trusted_identity(recipient_id, identity_key)

    def load_pre_key(self, pre_key_id: int) -> PreKeyRecord:
        return self.pre_key_store.load_pre_key(pre_key_id)

    def store_pre_key(self, pre_key_id: int, pre_key_record: PreKeyRecord) -> None:
        self.pre_key_store.store_pre_key(pre_key_id, pre_key_record)

    def contains_pre_key(self, pre_key_id: int) -> bool:
        return self.pre_key_store.contains_pre_key(pre_key_id)

    def remove_pre_key(self, pre_key_id: int) -> None:
        self.pre_key_store.remove_pre_key(pre_key_id)

    def load_session(self, recipient_id: str, device_id: int) -> SessionRecord:
        return self.session_store.load_session(recipient_id, device_id)

    def store_session(
        self, recipient_id: str, device_id: int, session_record: SessionRecord
    ) -> None:
        self.session_store.store_session(recipient_id, device_id, session_record)

    def contains_session(self, recipient_id: str, device_id: int) -> bool:
        return self.session_store.contains_session(recipient_id, device_id)

    def delete_session(self, recipient_id: str, device_id: int) -> None:
        self.session_store.delete_session(recipient_id, device_id)

    def delete_all_sessions(self, recipient_id: str) -> None:
        self.session_store.delete_all_sessions(recipient_id)

    def load_signed_pre_key(self, signed_pre_key_id: int) -> SignedPreKeyRecord:
        return self.signed_pre_key_store.load_signed_pre_key(signed_pre_key_id)

    def load_signed_pre_keys(self) -> list[SignedPreKeyRecord]:
        return self.signed_pre_key_store.load_signed_pre_keys()

    def store_signed_pre_key(
        self, signed_pre_key_id: int, signed_pre_key_record: SignedPreKeyRecord
    ) -> None:
        self.signed_pre_key_store.store_signed_pre_key(
            signed_pre_key_id, signed_pre_key_record
        )

    def contains_signed_pre_key(self, signed_pre_key_id: int) -> bool:
        return self.signed_pre_key_store.contains_signed_pre_key(signed_pre_key_id)

    def remove_signed_pre_key(self, signed_pre_key_id: int) -> None:
        self.signed_pre_key_store.remove_signed_pre_key(signed_pre_key_id)
