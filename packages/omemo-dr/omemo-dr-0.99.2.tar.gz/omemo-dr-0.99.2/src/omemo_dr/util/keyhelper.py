from __future__ import annotations

import binascii
import math
import os
import time

from ..ecc.curve import Curve
from ..identitykey import IdentityKey
from ..identitykeypair import IdentityKeyPair
from ..state.prekeyrecord import PreKeyRecord
from ..state.signedprekeyrecord import SignedPreKeyRecord
from .medium import Medium


class KeyHelper:
    @staticmethod
    def generate_identity_key_pair() -> IdentityKeyPair:
        """
        Generate an identity key pair. Clients should only do this once,
        at install time.
        @return the generated IdentityKeyPair.
        """
        key_pair = Curve.generate_key_pair()
        public_key = IdentityKey(key_pair.get_public_key())
        identity_key_pair = IdentityKeyPair.new(public_key, key_pair.get_private_key())
        return identity_key_pair

    @staticmethod
    def generate_device_id() -> int:
        """
        Generate a registration ID.  Clients should only do this once,
        at install time.
        """
        regId = KeyHelper.get_random_sequence()
        return regId

    @staticmethod
    def get_random_sequence(max: int = 4294967296) -> int:
        size = int(math.log(max) / math.log(2)) / 8
        rand = os.urandom(int(size))
        randh = binascii.hexlify(rand)
        return int(randh, 16)

    @staticmethod
    def generate_pre_keys(start: int, count: int) -> list[PreKeyRecord]:
        """
        Generate a list of PreKeys.  Clients should do this at install time, and
        subsequently any time the list of PreKeys stored on the server runs low.

        PreKey IDs are shorts, so they will eventually be repeated.
        Clients should store PreKeys in a circular buffer, so that they are
        repeated as infrequently as possible.
        """
        results: list[PreKeyRecord] = []
        start -= 1
        for i in range(0, count):
            pre_key_id = ((start + i) % (Medium.MAX_VALUE - 1)) + 1
            results.append(PreKeyRecord.new(pre_key_id, Curve.generate_key_pair()))

        return results

    @staticmethod
    def generate_signed_pre_key(
        identity_key_pair: IdentityKeyPair, signed_pre_key_id: int
    ) -> SignedPreKeyRecord:
        key_pair = Curve.generate_key_pair()
        signature = Curve.calculate_signature(
            identity_key_pair.get_private_key(), key_pair.get_public_key().serialize()
        )

        spk = SignedPreKeyRecord.new(
            signed_pre_key_id, int(round(time.time() * 1000)), key_pair, signature
        )

        return spk
