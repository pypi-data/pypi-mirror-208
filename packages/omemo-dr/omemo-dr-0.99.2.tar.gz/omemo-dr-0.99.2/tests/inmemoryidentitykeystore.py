from __future__ import annotations

from omemo_dr.ecc.curve import Curve
from omemo_dr.identitykey import IdentityKey
from omemo_dr.identitykeypair import IdentityKeyPair
from omemo_dr.util.keyhelper import KeyHelper


class InMemoryIdentityKeyStore:
    def __init__(self) -> None:
        self.trusted_keys: dict[str, IdentityKey] = {}
        identity_key_pair_keys = Curve.generate_key_pair()
        self.identity_key_pair = IdentityKeyPair.new(
            IdentityKey(identity_key_pair_keys.get_public_key()),
            identity_key_pair_keys.get_private_key(),
        )
        self.our_device_id = KeyHelper.generate_device_id()

    def get_identity_key_pair(self) -> IdentityKeyPair:
        return self.identity_key_pair

    def get_our_device_id(self) -> int:
        return self.our_device_id

    def save_identity(self, recipient_id: str, identity_key: IdentityKey) -> None:
        self.trusted_keys[recipient_id] = identity_key

    def is_trusted_identity(self, recipient_id: str, identity_key: IdentityKey) -> bool:
        if recipient_id not in self.trusted_keys:
            return True
        return self.trusted_keys[recipient_id] == identity_key
