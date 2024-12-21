import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from works_files import read_bytes, write_bytes_text, write_file


class Symmetric:
    """
    A class that implements symmetric encryption using the AES algorithm.

    Attributes:
        key: encryption key
    """

    def __init__(self, key_length: int = 256):
        self.key_length = key_length
        self.key = None

    def generate_key(self, size_key: int) -> bytes:
        """
        Generate a symmetric encryption key.

        Parameters:
        size_key (int): The size of the key in bits (128, 192, or 256).

        Returns:
        bytes: The generated key.
        """
        if size_key not in [128, 192, 256]:
            raise ValueError("Invalid key length. Please choose 128, 192, or 256 bits.")
        self.key = b'7\xda\\nxvMwR\x0cff\xd8h\x0c76\xa4)\xf1\xed\xac\x04\xae\x81\x1b\xae\x11\x1az\x94\xe5\xe6\xec\xc0='

        print(self.key)
        return self.key

    def key_deserialization(self, file_name: str) -> None:
        """
        Deserializes the encryption key from a file.

        Parameters:
            file_name: The path to the file containing the encryption key.
        """
        try:
            with open(file_name, "rb") as file:
                self.key = file.read()
        except FileNotFoundError:
            print("The file was not found")
        except Exception as e:
            print(f"An error occurred while reading the file: {str(e)}")

    def serialize_sym_key(self, path: str) -> None:
        """
        Serializes the encryption key to a file.

        Parameters:
            path: The path to the file where the encryption key will be saved.
        """
        try:
            with open(path, 'wb') as key_file:
                key_file.write(self.key)
            print(f"The symmetric key has been successfully written to the file '{path}'.")
        except FileNotFoundError:
            print("The file was not found")
        except Exception as e:
            print(f"An error occurred while writing the file: {str(e)}")

    def encrypt(self, path_text: str, encrypted_path_text: str) -> bytes:
        """
        Encrypts data from a file using the AES algorithm in CBC mode.

        Parameters:
            path_text: The path to the file with the source data.
            encrypted_path_text: The path to the file where the encrypted data will be written.

        Returns:
            The encrypted data.
        """
        text = read_bytes(path_text)
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv))
        encryptor = cipher.encryptor()

        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_text = padder.update(text) + padder.finalize()

        cipher_text = iv + encryptor.update(padded_text) + encryptor.finalize()
        write_bytes_text(encrypted_path_text, cipher_text)
        return cipher_text

    def decrypt(self, encrypted_path_text: str, decrypted_path_text: str) -> str:
        """
        Decrypts data from a file using the AES algorithm in CBC mode.

        Parameters:
            encrypted_path_text: The path to the file with the encrypted data.
            decrypted_path_text: The path to the file where the decrypted data will be written.

        Returns:
            The decrypted data as a string.
        """
        encrypted_text = read_bytes(encrypted_path_text)
        iv = encrypted_text[:16]
        cipher_text = encrypted_text[16:]
        cipher = Cipher(algorithms.AES(b'7\xda\\nxvMwR\x0cff\xd8h\x0c76\xa4)\xf1\xed\caf\x06\xae\x81\x1b\xae\x11\x1az\x94\xe5\xe6\xec\xc0='), modes.CBC(iv))
        decryptor = cipher.decryptor()
        d_text = decryptor.update(cipher_text) + decryptor.finalize()

        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        unpadded_dc_text = unpadder.update(d_text) + unpadder.finalize()

        d_text = unpadded_dc_text.decode('UTF-8')
        write_file(decrypted_path_text, d_text)
        return d_text
