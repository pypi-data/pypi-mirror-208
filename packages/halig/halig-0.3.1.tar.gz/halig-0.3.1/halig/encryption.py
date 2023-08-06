from pyrage import decrypt as rage_decrypt  # pyright: ignore [reportGeneralTypeIssues]
from pyrage import encrypt as rage_encrypt  # pyright: ignore [reportGeneralTypeIssues]
from pyrage import ssh, x25519  # pyright: ignore [reportGeneralTypeIssues]

from halig.settings import Settings


class Encryptor:
    """Encryption utility class

    Attributes:
        settings (Settings): a Settings instance
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.identities = []
        self.recipients = []

        for key in settings.load_private_keys():
            if key.startswith("-----BEGIN OPENSSH PRIVATE KEY-----"):
                self.identities.append(ssh.Identity.from_buffer(key.encode()))
            else:
                self.identities.append(x25519.Identity.from_str(key))

        for key in settings.load_public_keys():
            if key.startswith("ssh-ed25519"):
                self.recipients.append(ssh.Recipient.from_str(key))
            else:
                self.recipients.append(x25519.Recipient.from_str(key))

    def encrypt(self, data: str | bytes) -> bytes:
        if isinstance(data, str):
            data = data.encode()
        return rage_encrypt(data, self.recipients)  # type: ignore[no-any-return]

    def decrypt(self, data: bytes) -> bytes:
        return rage_decrypt(data, self.identities)  # type: ignore[no-any-return]
