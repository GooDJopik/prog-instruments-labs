import pytest
from unittest.mock import patch, mock_open
from cryptography.hazmat.primitives.asymmetric import rsa
from asymmetric import Asymmetric
import os


@pytest.fixture
def asymmetric_instance():
    """Fixture to create an Asymmetric instance with generated keys."""
    asym = Asymmetric()
    asym.generate_keys()
    return asym


def test_generate_keys(asymmetric_instance):
    """Test key generation."""
    assert asymmetric_instance.private_key is not None
    assert asymmetric_instance.public_key is not None
    assert isinstance(asymmetric_instance.private_key, rsa.RSAPrivateKey)
    assert isinstance(asymmetric_instance.public_key, rsa.RSAPublicKey)


def test_serialization_public_success(asymmetric_instance, capsys):
    """Test successful public key serialization."""
    with patch("builtins.open", mock_open()) as mock_file:
        asymmetric_instance.serialization_public("test_public.pem")
        mock_file.assert_called_with("test_public.pem", "wb")
        mock_file().write.assert_called_once()
        captured = capsys.readouterr()
        assert "The public key has been successfully written to the file" in captured.out


def test_serialization_private_success(asymmetric_instance, capsys):
    """Test successful private key serialization."""
    with patch("builtins.open", mock_open()) as mock_file:
        asymmetric_instance.serialization_private("test_private.pem")
        mock_file.assert_called_with("test_private.pem", "wb")
        mock_file().write.assert_called_once()
        captured = capsys.readouterr()
        assert "The private key has been successfully written to the file" in captured.out


@pytest.mark.parametrize(
    "key_type, serialization_method, deserialization_method, file_extension",
    [
        ("public", "serialization_public", "public_key_deserialization", "public.pem"),
        ("private", "serialization_private", "private_key_deserialization", "private.pem"),
    ],
)
def test_serialization_deserialization_cycle(
        asymmetric_instance, key_type, serialization_method, deserialization_method, file_extension, tmp_path
):
    """Test serialization and deserialization cycle for both public and private keys."""
    file_path = str(tmp_path / file_extension)

    getattr(asymmetric_instance, serialization_method)(file_path)

    asymmetric_deserialized = Asymmetric()

    getattr(asymmetric_deserialized, deserialization_method)(file_path)

    if key_type == "public":
        assert asymmetric_deserialized.public_key is not None
        assert isinstance(asymmetric_deserialized.public_key, rsa.RSAPublicKey)
    elif key_type == "private":
        assert asymmetric_deserialized.private_key is not None
        assert isinstance(asymmetric_deserialized.private_key, rsa.RSAPrivateKey)


def test_encrypt_decrypt_cycle(asymmetric_instance):
    """Test encryption and decryption cycle."""
    symmetric_key = os.urandom(32)
    encrypted_key = asymmetric_instance.encrypt(symmetric_key)
    decrypted_key = asymmetric_instance.decrypt(encrypted_key)
    assert symmetric_key == decrypted_key


def test_decrypt_invalid_key(asymmetric_instance):
    """Test decryption with an invalid key."""
    symmetric_key = os.urandom(32)
    encrypted_key = asymmetric_instance.encrypt(symmetric_key)

    invalid_asymmetric = Asymmetric()
    invalid_asymmetric.generate_keys()

    with pytest.raises(ValueError):
        invalid_asymmetric.decrypt(encrypted_key)
