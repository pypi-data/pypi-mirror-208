import unittest

from omemo_dr.ecc.curve import Curve
from omemo_dr.identitykey import IdentityKey
from omemo_dr.identitykeypair import IdentityKeyPair
from omemo_dr.protocol.prekeywhispermessage import PreKeyWhisperMessage
from omemo_dr.protocol.whispermessage import WhisperMessage
from omemo_dr.ratchet.aliceparameters import AliceParameters
from omemo_dr.ratchet.bobparameters import BobParameters
from omemo_dr.ratchet.ratchetingsession import RatchetingSession
from omemo_dr.sessioncipher import SessionCipher
from omemo_dr.state.sessionrecord import SessionRecord
from omemo_dr.state.sessionstate import SessionState
from omemo_dr.util.keyhelper import KeyHelper

from .inmemorystore import InMemoryStore


class SessionCipherTest(unittest.TestCase):
    def test_basic_session_v3(self):
        alice_session_record = SessionRecord()
        bob_session_record = SessionRecord()
        self._initialize_sessions_v3(
            alice_session_record.get_session_state(),
            bob_session_record.get_session_state(),
        )
        self._run_interaction(alice_session_record, bob_session_record)

    def _run_interaction(
        self, alice_session_record: SessionRecord, bob_session_record: SessionRecord
    ) -> None:
        alice_store = InMemoryStore()
        bob_store = InMemoryStore()

        alice_store.store_session("bob", 1, alice_session_record)
        bob_store.store_session("alice", 1, bob_session_record)

        alice_cipher = SessionCipher(alice_store, "bob", 1)
        bob_cipher = SessionCipher(bob_store, "alice", 1)

        alice_plaintext = "This is a plaintext message."
        message = alice_cipher.encrypt(alice_plaintext)
        bob_plaintext = bob_cipher.decrypt_msg(
            WhisperMessage.from_bytes(message.serialize())
        )

        bob_plaintext = bob_plaintext.decode()
        self.assertEqual(alice_plaintext, bob_plaintext)

        bob_reply = "This is a message from Bob."
        reply = bob_cipher.encrypt(bob_reply)
        received_reply = alice_cipher.decrypt_msg(
            WhisperMessage.from_bytes(reply.serialize())
        )
        received_reply = received_reply.decode()

        self.assertEqual(bob_reply, received_reply)

        alice_ciphertext_messages: list[WhisperMessage | PreKeyWhisperMessage] = []
        alice_plaintext_messages: list[str] = []

        for i in range(0, 50):
            alice_plaintext_messages.append("смерть за смерть %s" % i)
            alice_ciphertext_messages.append(
                alice_cipher.encrypt("смерть за смерть %s" % i)
            )

        for i in range(0, int(len(alice_ciphertext_messages) / 2)):
            received_plaintext = bob_cipher.decrypt_msg(
                WhisperMessage.from_bytes(alice_ciphertext_messages[i].serialize())
            )
            self.assertEqual(received_plaintext.decode(), alice_plaintext_messages[i])

    def _initialize_sessions_v3(
        self, alice_session_state: SessionState, bob_session_state: SessionState
    ) -> None:
        alice_identity_key_pair = Curve.generate_key_pair()
        alice_identity_key = IdentityKeyPair.new(
            IdentityKey(alice_identity_key_pair.get_public_key()),
            alice_identity_key_pair.get_private_key(),
        )
        alice_base_key = Curve.generate_key_pair()

        bob_identity_key_pair = Curve.generate_key_pair()
        bob_identity_key = IdentityKeyPair.new(
            IdentityKey(bob_identity_key_pair.get_public_key()),
            bob_identity_key_pair.get_private_key(),
        )
        bob_base_key = Curve.generate_key_pair()
        bob_ephemeral_key = bob_base_key
        bob_one_time_pre_key = KeyHelper.generate_pre_keys(1, 1)[0]

        alice_parameters = AliceParameters(
            alice_identity_key,
            alice_base_key,
            bob_identity_key.get_public_key(),
            bob_base_key.get_public_key(),
            bob_ephemeral_key.get_public_key(),
            bob_one_time_pre_key.get_key_pair().get_public_key(),
        )

        bob_parameters = BobParameters(
            bob_identity_key,
            bob_base_key,
            bob_ephemeral_key,
            bob_one_time_pre_key.get_key_pair(),
            alice_identity_key.get_public_key(),
            alice_base_key.get_public_key(),
        )

        RatchetingSession.initialize_session_as_alice(
            alice_session_state, 3, alice_parameters
        )
        RatchetingSession.initialize_session_as_bob(
            bob_session_state, 3, bob_parameters
        )
