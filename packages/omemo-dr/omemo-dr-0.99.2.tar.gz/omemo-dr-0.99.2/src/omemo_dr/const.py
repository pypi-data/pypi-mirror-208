from enum import IntEnum

NS_OMEMO_TMP = "eu.siacs.conversations.axolotl"
NS_OMEMO_2 = "urn:xmpp:omemo:2"

LEGACY_ENCODED_KEY_LENGTH = 33
ENCODED_KEY_LENGTH = 32


class OMEMOTrust(IntEnum):
    UNTRUSTED = 0
    VERIFIED = 1
    UNDECIDED = 2
    BLIND = 3
