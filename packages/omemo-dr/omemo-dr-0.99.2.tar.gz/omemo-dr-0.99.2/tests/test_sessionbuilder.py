import time
import unittest

from omemo_dr.const import NS_OMEMO_TMP
from omemo_dr.ecc.curve import Curve
from omemo_dr.exceptions import InvalidKeyException
from omemo_dr.protocol.ciphertextmessage import CiphertextMessage
from omemo_dr.protocol.prekeywhispermessage import PreKeyWhisperMessage
from omemo_dr.protocol.whispermessage import WhisperMessage
from omemo_dr.sessionbuilder import SessionBuilder
from omemo_dr.sessioncipher import SessionCipher
from omemo_dr.state.prekeybundle import PreKeyBundle
from omemo_dr.state.prekeyrecord import PreKeyRecord
from omemo_dr.state.signedprekeyrecord import SignedPreKeyRecord

from .inmemoryidentitykeystore import InMemoryIdentityKeyStore
from .inmemorystore import InMemoryStore
from .inmemorystore import Store

ALICE_RECIPIENT_ID = "alice"
BOB_RECIPIENT_ID = "bob"


class SessionBuilderTest(unittest.TestCase):
    def test_basic_pre_key_v3(self):
        # Prepare Bob Store
        bob_store = InMemoryStore()
        bob_pre_key_pair = Curve.generate_key_pair()
        bob_signed_pre_key_pair = Curve.generate_key_pair()
        bob_signed_pre_key_signature = Curve.calculate_signature(
            bob_store.get_identity_key_pair().get_private_key(),
            bob_signed_pre_key_pair.get_public_key().serialize(),
        )

        bob_pre_key = PreKeyBundle(
            1,
            NS_OMEMO_TMP,
            31337,
            bob_pre_key_pair.get_public_key(),
            22,
            bob_signed_pre_key_pair.get_public_key(),
            bob_signed_pre_key_signature,
            bob_store.get_identity_key_pair().get_public_key(),
        )

        bob_store.store_pre_key(
            31337, PreKeyRecord.new(bob_pre_key.get_pre_key_id(), bob_pre_key_pair)
        )
        bob_store.store_signed_pre_key(
            22,
            SignedPreKeyRecord.new(
                22,
                int(time.time() * 1000),
                bob_signed_pre_key_pair,
                bob_signed_pre_key_signature,
            ),
        )

        alice_store = InMemoryStore()
        alice_session_builder = SessionBuilder(
            alice_store,
            BOB_RECIPIENT_ID,
            1,
        )

        # Process PreKeyBundle and prepare message
        alice_session_builder.process_pre_key_bundle(bob_pre_key)
        self.assertTrue(alice_store.contains_session(BOB_RECIPIENT_ID, 1))
        self.assertTrue(
            alice_store.load_session(BOB_RECIPIENT_ID, 1)
            .get_session_state()
            .get_session_version()
            == 3
        )

        original_message = "L'homme est condamné à être libre"
        alice_session_cipher = SessionCipher(
            alice_store,
            BOB_RECIPIENT_ID,
            1,
        )
        outgoing_pk_message = alice_session_cipher.encrypt(original_message)
        self.assertTrue(outgoing_pk_message.get_type() == CiphertextMessage.PREKEY_TYPE)

        # Receive PreKeyMessage
        incoming_pk_message = PreKeyWhisperMessage.from_bytes(
            outgoing_pk_message.serialize()
        )
        bob_session_cipher = SessionCipher(bob_store, ALICE_RECIPIENT_ID, 1)
        plaintext = bob_session_cipher.decrypt_pkmsg(incoming_pk_message)
        plaintext = plaintext.decode()

        self.assertEqual(original_message, plaintext)
        self.assertTrue(bob_store.contains_session(ALICE_RECIPIENT_ID, 1))
        self.assertTrue(
            bob_store.load_session(ALICE_RECIPIENT_ID, 1)
            .get_session_state()
            .get_session_version()
            == 3
        )

        # Bob prepares message
        bob_outgoing_message = bob_session_cipher.encrypt(original_message)
        self.assertTrue(
            bob_outgoing_message.get_type() == CiphertextMessage.WHISPER_TYPE
        )

        # Alice receives message
        alice_plaintext = alice_session_cipher.decrypt_msg(
            WhisperMessage.from_bytes(bob_outgoing_message.serialize())
        )
        alice_plaintext = alice_plaintext.decode()

        self.assertEqual(alice_plaintext, original_message)

        self._run_interaction(alice_store, bob_store)

    def test_bad_signed_pre_key_signature(self):
        alice_store = InMemoryStore()
        alice_session_builder = SessionBuilder(
            alice_store,
            BOB_RECIPIENT_ID,
            1,
        )

        bob_identity_key_store = InMemoryIdentityKeyStore()

        bob_pre_key_pair = Curve.generate_key_pair()
        bob_signed_pre_key_pair = Curve.generate_key_pair()
        bob_signed_pre_key_signature = Curve.calculate_signature(
            bob_identity_key_store.get_identity_key_pair().get_private_key(),
            bob_signed_pre_key_pair.get_public_key().serialize(),
        )

        for i in range(0, len(bob_signed_pre_key_signature) * 8):
            modified_signature = bytearray(bob_signed_pre_key_signature[:])
            modified_signature[int(i / 8)] ^= 0x01 << (i % 8)

            bob_pre_key = PreKeyBundle(
                1,
                NS_OMEMO_TMP,
                31337,
                bob_pre_key_pair.get_public_key(),
                22,
                bob_signed_pre_key_pair.get_public_key(),
                bytes(modified_signature),
                bob_identity_key_store.get_identity_key_pair().get_public_key(),
            )

            with self.assertRaises(InvalidKeyException):
                alice_session_builder.process_pre_key_bundle(bob_pre_key)

        bob_pre_key = PreKeyBundle(
            1,
            NS_OMEMO_TMP,
            31337,
            bob_pre_key_pair.get_public_key(),
            22,
            bob_signed_pre_key_pair.get_public_key(),
            bob_signed_pre_key_signature,
            bob_identity_key_store.get_identity_key_pair().get_public_key(),
        )

        alice_session_builder.process_pre_key_bundle(bob_pre_key)

    def _run_interaction(self, alice_store: Store, bob_store: Store) -> None:
        alice_session_cipher = SessionCipher(
            alice_store,
            BOB_RECIPIENT_ID,
            1,
        )
        bob_session_cipher = SessionCipher(bob_store, ALICE_RECIPIENT_ID, 1)

        original_message = "smert ze smert"
        alice_message = alice_session_cipher.encrypt(original_message)

        self.assertTrue(alice_message.get_type() == CiphertextMessage.WHISPER_TYPE)

        plaintext = bob_session_cipher.decrypt_msg(
            WhisperMessage.from_bytes(alice_message.serialize())
        )
        plaintext = plaintext.decode()
        self.assertEqual(plaintext, original_message)

        bob_message = bob_session_cipher.encrypt(original_message)

        self.assertTrue(bob_message.get_type() == CiphertextMessage.WHISPER_TYPE)

        plaintext = alice_session_cipher.decrypt_msg(
            WhisperMessage.from_bytes(bob_message.serialize())
        )
        plaintext = plaintext.decode()
        self.assertEqual(plaintext, original_message)

        for i in range(0, 10):
            looping_message = (
                "What do we mean by saying that existence precedes essence? "
                "We mean that man first of all exists, encounters himself, "
                "surges up in the world--and defines himself aftward. %s" % i
            )
            alice_looping_message = alice_session_cipher.encrypt(looping_message)
            looping_plaintext = bob_session_cipher.decrypt_msg(
                WhisperMessage.from_bytes(alice_looping_message.serialize())
            )
            looping_plaintext = looping_plaintext.decode()
            self.assertEqual(looping_plaintext, looping_message)

        for i in range(0, 10):
            looping_message = (
                "What do we mean by saying that existence precedes essence? "
                "We mean that man first of all exists, encounters himself, "
                "surges up in the world--and defines himself aftward. %s" % i
            )
            bob_looping_message = bob_session_cipher.encrypt(looping_message)

            looping_plaintext = alice_session_cipher.decrypt_msg(
                WhisperMessage.from_bytes(bob_looping_message.serialize())
            )
            looping_plaintext = looping_plaintext.decode()
            self.assertEqual(looping_plaintext, looping_message)

        alice_out_of_order_messages: list[
            tuple[str, WhisperMessage | PreKeyWhisperMessage]
        ] = []

        for i in range(0, 10):
            looping_message = (
                "What do we mean by saying that existence precedes essence? "
                "We mean that man first of all exists, encounters himself, "
                "surges up in the world--and defines himself aftward. %s" % i
            )
            alice_looping_message = alice_session_cipher.encrypt(looping_message)
            alice_out_of_order_messages.append((looping_message, alice_looping_message))

        for i in range(0, 10):
            looping_message = (
                "What do we mean by saying that existence precedes essence? "
                "We mean that man first of all exists, encounters himself, "
                "surges up in the world--and defines himself aftward. %s" % i
            )
            alice_looping_message = alice_session_cipher.encrypt(looping_message)
            looping_plaintext = bob_session_cipher.decrypt_msg(
                WhisperMessage.from_bytes(alice_looping_message.serialize())
            )
            looping_plaintext = looping_plaintext.decode()
            self.assertEqual(looping_plaintext, looping_message)

        for i in range(0, 10):
            looping_message = "You can only desire based on what you know: %s" % i
            bob_looping_message = bob_session_cipher.encrypt(looping_message)

            looping_plaintext = alice_session_cipher.decrypt_msg(
                WhisperMessage.from_bytes(bob_looping_message.serialize())
            )
            looping_plaintext = looping_plaintext.decode()
            self.assertEqual(looping_plaintext, looping_message)

        for alice_out_of_order_message in alice_out_of_order_messages:
            out_of_order_plaintext = bob_session_cipher.decrypt_msg(
                WhisperMessage.from_bytes(alice_out_of_order_message[1].serialize())
            )
            out_of_order_plaintext = out_of_order_plaintext.decode()
            self.assertEqual(out_of_order_plaintext, alice_out_of_order_message[0])
