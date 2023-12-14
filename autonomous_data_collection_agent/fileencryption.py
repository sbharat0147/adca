# The `FileEncryption` class provides methods for encrypting and decrypting files using the Fernet
# encryption algorithm.

from cryptography.fernet import Fernet
from autonomous_data_collection_agent import ERRORS, __app_name__, __version__, config
import configparser
import typer
import os
import ast

class FileEncryption:
    def __init__(self) -> None:
        """
        The function initializes a class instance by reading a configuration file and setting encryption
        key and encryption enabled properties.
        """
        if os.path.isfile(config.CONFIG_FILE_PATH):
            self._config_parser = configparser.ConfigParser()
            # Read the existing file first
            self._config_parser.read(config.CONFIG_FILE_PATH)
            # Add the new section
            self._encryption_key = ast.literal_eval(self._config_parser["Encryption"]["key"])
            self._encryption_enabled = self._config_parser["Encryption"]["enabled"]
        else:
            typer.secho(
                'Config file not found. Please, run "autonomous_data_collection_agent init"',
                fg=typer.colors.RED,
            )
            raise typer.Exit(1)

    def check_if_enabled(self):
        """
        The function checks if encryption is enabled by comparing the value of the `_encryption_enabled`
        attribute to the string "True".
        :return: a boolean value. If the `_encryption_key` is `None`, it will return `False`. Otherwise,
        it will return the result of comparing the `_encryption_enabled` attribute to the string "True".
        """
        if self._encryption_key is None:
            return False
        
        return self._encryption_enabled == "True"
     
    def _check_if_enabled(self):
        """
        The function checks if encryption is enabled by verifying the availability of an encryption key.
        :return: the value of the expression `self._encryption_enabled == "True"`.
        """
        if self._encryption_key is None:
            typer.secho(
                'Encryption key is not available. Please, run "autonomous_data_collection_agent init"',
                fg=typer.colors.RED,
            )
            raise typer.Exit(1)
        
        return self._encryption_enabled == "True"
    
    def encypt_and_save_content(self, file_content, file_path):
        """
        The function `encypt_and_save_content` encrypts the given file content using a provided
        encryption key and saves it to the specified file path.
        
        :param file_content: The `file_content` parameter is the content of the file that you want to
        encrypt and save. It should be a string or bytes object
        :param file_path: The `file_path` parameter is the path where the encrypted file will be saved.
        It should include the file name and extension. For example, "C:/Documents/encrypted_file.txt"
        :return: the file path where the encrypted content is saved.
        """
        if self._check_if_enabled():
            fernet = Fernet(self._encryption_key)

            if not os.path.exists(file_path):
                open(file_path, 'a').close()

            if os.path.isfile(file_path):
                # encrypting the file
                encrypted = fernet.encrypt(file_content)
                
                # opening the file in write mode and 
                # writing the encrypted data
                with open(file_path, 'wb') as encrypted_file:
                    encrypted_file.write(encrypted)

                return file_path
            else:
                typer.secho(
                    'Please check File Path.',
                    fg=typer.colors.RED,
                )
        else:
            typer.secho(
                'Encryption is not enabled. Please, run "autonomous_data_collection_agent enable-encryption" .',
                fg=typer.colors.RED,
            )
    
    def encypt_original_file(self, file_path):
        """
        The function `encrypt_original_file` encrypts a file using the Fernet encryption algorithm and
        saves the encrypted data back to the original file.
        
        :param file_path: The `file_path` parameter is the path to the file that you want to encrypt
        :return: the file path of the encrypted file.
        """
        if self._check_if_enabled():
            fernet = Fernet(self._encryption_key)
            if os.path.isfile(file_path):
                # opening the original file to encrypt
                with open(file_path, 'rb') as file:
                    original = file.read()
                # encrypting the file
                encrypted = fernet.encrypt(original)
              
                # opening the file in write mode and 
                # writing the encrypted data
                with open(file_path, 'wb') as encrypted_file:
                    encrypted_file.write(encrypted)

                return file_path
            else:
                typer.secho(
                    fg=typer.colors.RED,
                )
        else:
            typer.secho(
                'Encryption is not enabled. Please, run "autonomous_data_collection_agent enable-encryption" .',
                fg=typer.colors.RED,
            )
    
    def encypt_file(self, source_file_path, destination_file_path):
        """
        The `encrypt_file` function takes a source file path and a destination file path, encrypts the
        contents of the source file using a provided encryption key, and writes the encrypted data to
        the destination file.
        
        :param source_file_path: The source_file_path parameter is the path to the file that you want to
        encrypt
        :param destination_file_path: The `destination_file_path` parameter is the path where the
        encrypted file will be saved
        :return: the destination file path.
        """
        if self._check_if_enabled():
            fernet = Fernet(self._encryption_key)
            if not os.path.exists(destination_file_path):
                open(destination_file_path, 'a').close()
            if os.path.isfile(source_file_path) and os.path.isfile(destination_file_path):
                # opening the original file to encrypt
                with open(source_file_path, 'rb') as file:
                    file_contnet = file.read()
                # encrypting the file
                encrypted = fernet.encrypt(file_contnet)
                
                # opening the file in write mode and 
                # writing the encrypted data
                with open(destination_file_path, 'wb') as encrypted_file:
                    encrypted_file.write(encrypted)

                return destination_file_path
            else:
                typer.secho(
                    'Please check Source/ Destination File Path.',
                    fg=typer.colors.RED,
                ) 
        else:
            typer.secho(
                'Encryption is not enabled. Please, run "autonomous_data_collection_agent enable-encryption" .',
                fg=typer.colors.RED,
            )
    
    def decypt_and_save_content(self, file_content, file_path):
        """
        The function `decrypt_and_save_content` takes a file content and a file path, decrypts the
        content using a provided encryption key, and saves the decrypted content to the specified file
        path.
        
        :param file_content: The content of the file that needs to be decrypted and saved
        :param file_path: The file path is the location where the decrypted content will be saved. It
        should be a string representing the file path, including the file name and extension
        :return: the file path where the decrypted content is saved.
        """
        if self._check_if_enabled():
            fernet = Fernet(self._encryption_key)

            if not os.path.exists(file_path):
                open(file_path, 'a').close()

            if os.path.isfile(file_path):
                # decrypting the file
                decrypted = fernet.encrypt(file_content)
                
                # opening the file in write mode and 
                # writing the decrypted data
                with open(file_path, 'wb') as decrypted_file:
                    decrypted_file.write(decrypted)

                return file_path
            else:
                typer.secho(
                    'Please check File Path.',
                    fg=typer.colors.RED,
                )
        else:
            typer.secho(
                'Encryption is not enabled. Please, run "autonomous_data_collection_agent enable-encryption" .',
                fg=typer.colors.RED,
            )
    
    def decypt_original_file(self, file_path):
        """
        The function `decrypt_original_file` decrypts a file using the Fernet encryption algorithm and
        overwrites the original file with the decrypted data.
        
        :param file_path: The `file_path` parameter is the path to the file that you want to decrypt
        :return: the file path of the decrypted file.
        """
        if self._check_if_enabled():
            fernet = Fernet(self._encryption_key)
            if os.path.isfile(file_path):
                # opening the original file to decrypt
                with open(file_path, 'rb') as file:
                    original = file.read()
                # decrypting the file
                decrypted = fernet.encrypt(original)
                # opening the file in write mode and 
                # writing the decrypted data
                with open(file_path, 'wb') as decrypted_file:
                    decrypted_file.write(decrypted)

                return file_path
            else:
                typer.secho(
                    'Please check File Path.',
                    fg=typer.colors.RED,
                )
        else:
            typer.secho(
                'Encryption is not enabled. Please, run "autonomous_data_collection_agent enable-encryption" .',
                fg=typer.colors.RED,
            )
    
    def decypt_file(self, source_file_path, destination_file_path):
        """
        The function `decrypt_file` takes a source file path and a destination file path, checks if
        encryption is enabled, and if so, decrypts the source file and writes the decrypted data to the
        destination file.
        
        :param source_file_path: The source_file_path parameter is the path to the file that you want to
        decrypt
        :param destination_file_path: The `destination_file_path` parameter is the path where the
        decrypted file will be saved
        :return: the destination file path.
        """
        if self._check_if_enabled():
            fernet = Fernet(self._encryption_key)

            if not os.path.exists(destination_file_path):
                open(destination_file_path, 'a').close()

            if os.path.isfile(source_file_path) and os.path.isfile(destination_file_path):
                # opening the original file to decrypt
                with open(source_file_path, 'rb') as file:
                    file_contnet = file.read()
                # decrypting the file
                decrypted = fernet.encrypt(file_contnet)
                
                # opening the file in write mode and 
                # writing the encrypted data
                with open(destination_file_path, 'wb') as decrypted_file:
                    decrypted_file.write(decrypted)

                return destination_file_path
            else:
                typer.secho(
                    'Please check Source/ Destination File Path.',
                    fg=typer.colors.RED,
                ) 
        else:
            typer.secho(
                'Encryption is not enabled. Please, run "autonomous_data_collection_agent enable-encryption" .',
                fg=typer.colors.RED,
            )