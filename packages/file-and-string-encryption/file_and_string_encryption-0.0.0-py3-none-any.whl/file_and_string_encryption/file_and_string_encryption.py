# -*- coding: utf-8 -*-

"""
Created on "Datum"

von: https://stackoverflow.com/questions/2490334/simple-way-to-encode-a-string-according-to-a-password
"""


### Fernet with password – key derived from password, weakens the security somewhat
# https://stackoverflow.com/questions/2490334/simple-way-to-encode-a-string-according-to-a-password

from base64 import urlsafe_b64decode as b64d
from base64 import urlsafe_b64encode as b64e
import os
from pathlib import Path
import binascii
from secrets import token_bytes as secrets_token_bytes, choice as secrets_choice
from string import ascii_letters, digits, punctuation

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from passlib.context import CryptContext
from easy_tasks import main_and_sub_progress_printer

backend = default_backend()
iterations = 100_000


def _derive_key(password: bytes, salt: bytes, iterations: int = iterations) -> bytes:
    """Derive a secret key from a given password and salt"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
        backend=backend,
    )
    return b64e(kdf.derive(password))


def password_encrypt_bytes(
    message: bytes, password: str, iterations: int = iterations
) -> bytes:
    salt = secrets_token_bytes(16)
    key = _derive_key(password.encode(), salt, iterations)
    return b64e(
        b"%b%b%b"
        % (
            salt,
            iterations.to_bytes(4, "big"),
            b64d(Fernet(key).encrypt(message)),
        )
    )


def encrypt_string_with_password(
    message: str, password: str, iterations: int = 100000
) -> bytes:
    """Encrypt a message using a password. Iterations have an influence on the safety, the higher the stonger the longer the computation time.

    Args:
        message (str): Message to encyrypt.
        password (str): Password to use.
        iterations (int, optional): Iterations have an influence on the safety, the higher the stonger the longer the computation time. Defaults to 100000.

    Returns:
        bytes: Encrypted message.
    """
    if type(message) != bytes:
        message = message.encode()
    salt = secrets_token_bytes(16)
    key = _derive_key(password.encode(), salt, iterations)
    return b64e(
        b"%b%b%b"
        % (
            salt,
            iterations.to_bytes(4, "big"),
            b64d(Fernet(key).encrypt(message)),
        )
    )


def decrypt_string_with_password(token: bytes, password: str) -> str:
    """Decrypt a message aka token using a password.

    Args:
        token (bytes): Your massage aka token.
        password (str): The password.

    Returns:
        str: The decrypted message.
    """
    decoded = b64d(token)
    salt, iter, token = decoded[:16], decoded[16:20], b64e(decoded[20:])
    iterations = int.from_bytes(iter, "big")
    key = _derive_key(password.encode(), salt, iterations)
    pw = Fernet(key).decrypt(token).decode()
    return pw


def password_decrypt_non_string(token: bytes, password: str):
    decoded = b64d(token)
    salt, iter, token = decoded[:16], decoded[16:20], b64e(decoded[20:])
    iterations = int.from_bytes(iter, "big")
    key = _derive_key(password.encode(), salt, iterations)
    pw = Fernet(key).decrypt(token).decode()
    return pw


def encrypt_secret(secret, password: str):
    """
    -> encrypted_secret, salt
    """
    salt = os.urandom(16)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=400000,
    )

    key = b64e(kdf.derive(password.encode()))

    f = Fernet(key)

    encrypted_secret = f.encrypt(secret.encode())

    return encrypted_secret, salt


def decrypt_secret(encrypted_secret, password: str, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=400000,
    )

    key = b64e(kdf.derive(password.encode()))

    f = Fernet(key)

    secret_msg = f.decrypt(encrypted_secret)
    secret_msg = secret_msg.decode()

    return secret_msg


def generate_password(length=16):
    chars = ascii_letters + punctuation + digits
    password = str()
    while True:
        password = "".join(secrets_choice(chars) for i in range(length))
        if (
            any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            # and sum(c.isdigit() for c in password) >= 3
            and any(c.isdigit() for c in password)
            and any(punctuation)
        ):
            break

    return password


def encrypt_image_alt(img_path: str, target_dir: str, password: str):
    BildName = os.path.basename(img_path)
    key = Fernet.generate_key()
    s_key = encrypt_string_with_password(key, password)
    pfad = os.path.join(target_dir, f"{BildName}_key.txt")
    with open(pfad, mode="wb") as keyValue:  # target_dir + f"/{BildName}_key.txt"
        keyValue.write(s_key)

    # Encrypt image
    with open(img_path, "rb") as f:
        content = f.read()
    hexValue = binascii.hexlify(content)

    f = Fernet(key)
    encHexVal = f.encrypt(hexValue)

    pfad = os.path.join(target_dir, f"{BildName}_encryptedHex.txt")
    with open(
        pfad, mode="wb"
    ) as hexValueFile:  # target_dir + f"/{BildName}_encryptedHex.txt"
        hexValueFile.write(encHexVal)

    # Verification checks
    a = f.decrypt(encHexVal)

    # hexed bytes is same encoding as 'ascii'
    pfad = os.path.join(target_dir, f"{BildName}_realValue.txt")
    with open(pfad, mode="wb") as writeHex:  # target_dir + f"/{BildName}_realValue.txt"
        originalHex = writeHex.write(hexValue)

    with open(
        pfad, mode="r", encoding="ascii"
    ) as reading:  # target_dir + f"/{BildName}_realValue.txt"
        realValue = reading.read()


def decrypt_image_alt(
    img_name: str, source_dir: str, password: str, ZielOrdner: str = ""
):
    if ZielOrdner == "":
        ZielOrdner = source_dir

    pfad = os.path.join(source_dir, f"{img_name}_key.txt")
    with open(pfad, mode="rb") as keyValue:
        s_key = keyValue.read()
        key = decrypt_string_with_password(s_key, password)
        f = Fernet(key)

    pfad = os.path.join(source_dir, f"{img_name}_encryptedHex.txt")
    with open(pfad, mode="rb") as imageHexValue:
        encHexValue = imageHexValue.read()
    hexValue = f.decrypt(encHexValue)
    binValue = binascii.unhexlify(hexValue)

    pfad = os.path.join(source_dir, f"{img_name}_realValue.txt")
    with open(pfad, mode="rb") as compare:
        realContents = compare.read()

    pfad = os.path.join(ZielOrdner, img_name)
    with open(pfad, "wb") as file:
        file.write(binValue)


def encrypt_image_with_password(img_path: str, target_dir: str, password: str):
    BildName = os.path.basename(img_path)

    # key
    key = Fernet.generate_key()
    s_key = encrypt_string_with_password(key, password)
    pfad = os.path.join(target_dir, f"{BildName}_key.txt")
    with open(pfad, mode="wb") as keyValue:
        keyValue.write(s_key)

    # Encrypt image
    with open(img_path, "rb") as f:
        content = f.read()
    hexValue = binascii.hexlify(content)

    f = Fernet(key)
    encHexVal = f.encrypt(hexValue)

    pfad = os.path.join(target_dir, f"{BildName}_encryptedHex.txt")
    with open(pfad, mode="wb") as hexValueFile:
        hexValueFile.write(encHexVal)

    # Verification checks
    a = f.decrypt(encHexVal)


def decrypt_image_with_password(
    to_be_img_path: str, encrypted_path: str, key_path: str, password: str
):
    with open(key_path, mode="rb") as keyValue:
        s_key = keyValue.read()
        key = decrypt_string_with_password(s_key, password)
        f = Fernet(key)

    with open(encrypted_path, mode="rb") as imageHexValue:
        encHexValue = imageHexValue.read()
    hexValue = f.decrypt(encHexValue)
    binValue = binascii.unhexlify(hexValue)

    with open(to_be_img_path, "wb") as file:
        file.write(binValue)


def hash_password_argon2(password: str, argon2_default_rounds=55):
    context = CryptContext(
        schemes=["argon2"],
        default="argon2",
        argon2__default_rounds=argon2_default_rounds,
    )
    hashed_password = context.hash(password)
    return hashed_password


def verfiy_hashed_password_argon2(
    password: str, hashed_password, argon2_default_rounds=55
):
    _cryptcontext = CryptContext(
        schemes=["argon2"],
        default="argon2",
        argon2__default_rounds=argon2_default_rounds,
    )
    crypt_check = _cryptcontext.verify(password, hashed_password)
    return crypt_check


def get_random_key():
    """Generate a random key.

    Returns:
        bytes: The key generated by Fernet.generate_key()
    """
    return Fernet.generate_key()


def encrypt_file_with_password(
    filepath: str,
    enc_filepath: str,
    password: str,
    keypath: str | None = None,
    error_if_enc_is_file: bool = True,
    error_if_key_is_file: bool = True,
):
    """Encrypt a file and save the encrypted key as a file. The key will be encrypted using a password and the function encrypt_string_with_password.

    Args:
        filepath (str): The path to the file.
        enc_filepath (str): The path for the encrypted file, including the filename.
        keypath (str | None): The path for the unprotected key, including the filename. Defaults to None, meaning it won't be saved.
        password (str): Your password.
    """
    if error_if_enc_is_file and os.path.isfile(enc_filepath):
        raise FileExistsError(
            f"There is already a file in the enc_filepath location.\n\tenc_filepath: {enc_filepath}"
        )
    if error_if_key_is_file and os.path.isfile(keypath):
        raise FileExistsError(
            f"There is already a file in the keypath location.\n\tkeypath: {keypath}"
        )
    key = Fernet.generate_key()
    encryptet_key = encrypt_string_with_password(key, password)
    if not os.path.isdir(os.path.dirname(enc_filepath)):
        os.makedirs(os.path.dirname(enc_filepath))
    if not os.path.isdir(os.path.dirname(keypath)):
        os.makedirs(os.path.dirname(keypath))
    with open(keypath, "wb") as f:
        f.write(encryptet_key)
    fernet = Fernet(key)
    with open(filepath, "rb") as original_file:
        original = original_file.read()
    encrypted = fernet.encrypt(original)
    with open(enc_filepath, "wb") as encrypted_file:
        encrypted_file.write(encrypted)


def encrypt_file(
    filepath: str,
    enc_filepath: str,
    keypath: str | None = None,
    key: bytes = None,
    error_if_enc_is_file: bool = True,
    error_if_key_is_file: bool = True,
):
    """Encrypt a file and save the unprotected key as a file under the specified location.

    Args:
        filepath (str): The path to the file.
        enc_filepath (str): The path for the encrypted file, including the filename.
        keypath (str | None): The path for the unprotected key, including the filename. Defaults to None, meaning it won't be saved.
        key (bytes, optional): You can reuse the key of earlier encryptions or generate a key using the function get_random_key. Defaults to None.
        error_if_enc_is_file (bool): Raise an exception if enc_filepath is already a file.
        error_if_key_is_file (bool): Raise an exception if keypath is already a file.

    Returns:
        bytes: The key generated by Fernet.generate_key()
    """
    if error_if_key_is_file and os.path.isfile(enc_filepath):
        raise FileExistsError(
            f"There is already a file in the enc_filepath location.\n\tenc_filepath: {enc_filepath}"
        )
    if key == None:
        key = Fernet.generate_key()
    if not os.path.isdir(os.path.dirname(enc_filepath)):
        os.makedirs(os.path.dirname(enc_filepath))
    if keypath != None:
        if not os.path.isdir(os.path.dirname(keypath)):
            os.makedirs(os.path.dirname(keypath))
        if error_if_enc_is_file and os.path.isfile(keypath):
            raise FileExistsError(
                f"There is already a file in the keypath location.\n\tkeypath: {keypath}"
            )
        with open(keypath, "wb") as f:
            f.write(key)
    fernet = Fernet(key)
    with open(filepath, "rb") as original_file:
        original = original_file.read()
    encrypted = fernet.encrypt(original)
    with open(enc_filepath, "wb") as encrypted_file:
        encrypted_file.write(encrypted)
    return key


def decrypt_file_with_password(
    to_be_filepath: str, enc_filepath: str, keypath: str, password: str
):
    """Decrypt a file using a password. The file was decrypted using encrypt_file_with_password.

    Args:
        to_be_filepath (str): The path at which the file shall be generated, including the filename.
        enc_filepath (str): The path to the encrypted file.
        keypath (str): The path to the encrypted key.
        password (str): The password to decrypt the actual key.
    """
    with open(keypath, "rb") as f:
        enc_key = f.read()
    key = decrypt_string_with_password(enc_key, password)
    fernet = Fernet(key)
    with open(enc_filepath, "rb") as encrypted_file:
        encrypted = encrypted_file.read()
    decrypted = fernet.decrypt(encrypted)
    filename, fileext = os.path.splitext(os.path.basename(to_be_filepath))
    basepath = os.path.dirname(to_be_filepath)
    if not os.path.isdir(basepath):
        os.makedirs(basepath)
    pre_filepath = os.path.join(basepath, filename)
    with open(pre_filepath, "wb") as decrypted_file:
        decrypted_file.write(decrypted)
    if os.path.isdir(to_be_filepath):
        os.removedirs(to_be_filepath)
    os.rename(pre_filepath, to_be_filepath)


def decrypt_file(
    to_be_filepath: str,
    enc_filepath: str,
    keypath: str | bytes,
    error_if_target_is_file: bool = True,
):
    """Decrypt a file using the generated key. The file was decrypted with encrypt_file.

    Args:
        to_be_filepath (str): The path at which the file shall be generated, including the filename.
        enc_filepath (str): The path to the encrypted file.
        keypath (str | bytes): The path to the key or alternativley the key itself.
    """
    if error_if_target_is_file and os.path.isfile(to_be_filepath):
        raise FileExistsError(
            f"There is already a file in the to_be_filepath location.\n\tto_be_filepath: {to_be_filepath}"
        )
    if isinstance(keypath, str):
        with open(keypath, "rb") as f:
            key = f.read()
    else:
        key = keypath
    fernet = Fernet(key)
    with open(enc_filepath, "rb") as encrypted_file:
        encrypted = encrypted_file.read()
    decrypted = fernet.decrypt(encrypted)
    filename, fileext = os.path.splitext(os.path.basename(to_be_filepath))
    basepath = os.path.dirname(to_be_filepath)
    if not os.path.isdir(basepath):
        os.makedirs(basepath)
    pre_filepath = os.path.join(basepath, filename)
    with open(pre_filepath, "wb") as decrypted_file:
        decrypted_file.write(decrypted)
    if os.path.isdir(to_be_filepath):
        os.removedirs(to_be_filepath)
    os.rename(pre_filepath, to_be_filepath)


def encrypt_directory(
    dir_path: str,
    enc_dir_path: str,
    keypath: str | None = None,
    key: bytes = None,
    error_if_enc_is_file: bool = True,
    error_if_key_is_file: bool = True,
):
    dir_path = os.path.normpath(dir_path)
    if key == None:
        key = get_random_key()

    l1 = len(list(os.walk(dir_path)))

    main_and_sub_progress_printer(
        0,
        l1,
        0,
        0,
        mainpre_string="Progress on dirpaths: ",
        subpre_string="Progress on files in current dir: ",
    )
    for main_index, (root, dirs, files) in enumerate(os.walk(dir_path)):
        sub_path = root.replace(dir_path, "")
        sub_path = sub_path.lstrip("\\")
        l2 = len(files)
        for sub_index, f in enumerate(files):
            fp = os.path.join(root, f)
            nfp = os.path.join(enc_dir_path, sub_path, f)
            encrypt_file(
                fp, nfp, keypath, key, error_if_enc_is_file, error_if_key_is_file
            )
            main_and_sub_progress_printer(
                main_index + 1,
                l1,
                sub_index + 1,
                l2,
                mainpre_string="Progress on dirpaths: ",
                subpre_string="Progress on files in current dir: ",
            )
    return key


def decrypt_directory(
    target_dir_path: str,
    enc_dir_path: str,
    keypath: str | None | bytes = None,
    error_if_target_is_file: bool = True,
):
    enc_dir_path = os.path.normpath(enc_dir_path)

    l1 = len(list(os.walk(enc_dir_path)))

    main_and_sub_progress_printer(
        0,
        l1,
        0,
        0,
        mainpre_string="Progress on dirpaths: ",
        subpre_string="Progress on files in current dir: ",
    )
    for main_index, (root, dirs, files) in enumerate(os.walk(enc_dir_path)):
        sub_path = root.replace(enc_dir_path, "")
        sub_path = sub_path.lstrip("\\")
        l2 = len(files)
        for sub_index, f in enumerate(files):
            fp = os.path.join(root, f)
            nfp = os.path.join(target_dir_path, sub_path, f)
            decrypt_file(nfp, fp, keypath, error_if_target_is_file)
            main_and_sub_progress_printer(
                main_index + 1,
                l1,
                sub_index + 1,
                l2,
                mainpre_string="Progress on dirpaths: ",
                subpre_string="Progress on files in current dir: ",
            )


def save_key(
    key: bytes,
    keypath: str,
    password: str | None = None,
    error_if_key_is_file: bool = True,
):
    """Save the key returned by an encryption function. Additionally you can encrypt the key by setting the password.

    Args:
        key (bytes): Key returned by an encryption function.
        keypath (str): The path for the key to be written to.
        password (str | None, optional): A password to encrypt the key. Defaults to None.
        error_if_key_is_file (bool, optional): Throw an exception if there already is a file. Defaults to True.

    Raises:
        FileExistsError: If keypath is occupied.
    """
    if error_if_key_is_file and os.path.isfile(keypath):
        raise FileExistsError(
            f"There is already a file in the keypath location.\n\tkeypath: {keypath}"
        )
    if password != None:
        encryptet_key = encrypt_string_with_password(key, password)
    else:
        encryptet_key = key
    keypath_parent = os.path.dirname(keypath)
    if not os.path.isdir(keypath_parent):
        os.makedirs(keypath_parent)
    with open(keypath, "wb") as f:
        f.write(encryptet_key)


if __name__ == "__main__":
    # encrypt_directory(
    #     r"Code Sammlung\Passwort",
    #     r"C:\Users\Creed\OneDrive\Schul-Dokumente\Programmieren\Python\Code Sammlung\mehr\test",
    #     r"C:\Users\Creed\OneDrive\Schul-Dokumente\Programmieren\Python\Code Sammlung\mehr\KEY",
    # )
    decrypt_directory(
        r"Code Sammlung\Passwort2",
        r"C:\Users\Creed\OneDrive\Schul-Dokumente\Programmieren\Python\Code Sammlung\mehr\test",
        r"C:\Users\Creed\OneDrive\Schul-Dokumente\Programmieren\Python\Code Sammlung\mehr\KEY",
    )
