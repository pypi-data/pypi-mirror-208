from cryptography.fernet import Fernet


class EncryptionUtil:
    def __init__(self, key):
        self.fernet = Fernet(key)

    def decrypt_file(self, encrypted_file='device.encrypted', decrypted_file='device.properties'):
        # opening the original file to decrypt
        with open(encrypted_file, 'rb') as enc_file:
            encrypted = enc_file.read()

        # encrypting the file
        decrypted = self.fernet.decrypt(encrypted)

        # writing the decrypted data
        with open(decrypted_file, 'wb') as dec_file:
            dec_file.write(decrypted)

    def encrypt_file(self, file_in='local.device.properties', file_out='device.encrypted'):
        # opening the original file to encrypt
        with open(file_in, 'rb') as file:
            original = file.read()

        # encrypting the file
        encrypted = self.fernet.encrypt(original)

        # writing the encrypted data
        with open(file_out, 'wb') as encrypted_file:
            encrypted_file.write(encrypted)
