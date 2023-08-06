from pyrage import decrypt, encrypt, x25519

from halig.encryption import Encryptor
from halig.settings import Settings


def test_instance_encryptor_from_age_keys(halig_path, notebooks_path):
    identity_paths = []
    recipient_paths = []
    identities = []
    for i in range(5):
        identity = x25519.Identity.generate()
        identities.append(identity)
        identity_path = halig_path / f"identity_{i}.key"
        identity_path.touch()
        with identity_path.open("w") as f:
            f.write(str(identity))
        identity_paths.append(identity_path)

        recipient_path = halig_path / f"recipient_{i}.key"
        recipient_path.touch()

        with recipient_path.open("w") as f:
            f.write(str(identity.to_public()))

        recipient_paths.append(recipient_path)

    settings = Settings(
        notebooks_root_path=notebooks_path,
        identity_paths=identity_paths,
        recipient_paths=recipient_paths,
    )
    encryptor = Encryptor(settings)
    for identity in identities:
        assert str(identity) in [str(identity) for identity in encryptor.identities]
        assert str(identity.to_public()) in [str(recipient) for recipient in encryptor.recipients]


def test_encrypt(encryptor: Encryptor, ssh_identity):
    unencrypted_data = "foo"
    encrypted_data = encryptor.encrypt(unencrypted_data)
    assert isinstance(encrypted_data, bytes)
    assert unencrypted_data == decrypt(encrypted_data, [ssh_identity]).decode()


def test_encrypt_bytes(encryptor: Encryptor, ssh_identity):
    unencrypted_data = b"foo"
    encrypted_data = encryptor.encrypt(unencrypted_data)

    assert isinstance(encrypted_data, bytes)
    assert unencrypted_data == decrypt(encrypted_data, [ssh_identity])


def test_decrypt(encryptor: Encryptor, ssh_recipient):
    unencrypted_data = "foo"
    encrypted_data = encrypt(unencrypted_data.encode(), [ssh_recipient])
    decrypted_data = encryptor.decrypt(encrypted_data)
    assert decrypted_data.decode() == unencrypted_data


def test_decrypt_bytes(encryptor: Encryptor, ssh_recipient):
    unencrypted_data = b"foo"
    encrypted_data = encrypt(unencrypted_data, [ssh_recipient])
    decrypted_data = encryptor.decrypt(encrypted_data)
    assert decrypted_data == unencrypted_data
