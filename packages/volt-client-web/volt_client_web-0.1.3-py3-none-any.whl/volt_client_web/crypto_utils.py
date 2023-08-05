from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.serialization import load_pem_public_key, PublicFormat, Encoding
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.backends import openssl
import base64
from hashlib import sha256
import base58
from datetime import datetime
import json
from os import urandom

def get_key(pemKey):
    """
    Gets private and public key data from serialized private key.

    Parameters
    ----------
    pemKey : str
        Serialized private key in PEM format.

    Returns
    -------
    Dict[str, object]
        A dictionary containing the private key and public key objects.

    """
    # load private key from PEM serialized private key
    privateKey = serialization.load_pem_private_key(
        pemKey.encode("ascii"), password=None
    ) 
    # get public key from private key
    publicKey = (
        privateKey.public_key()
    )
    return {"privateKey": privateKey, "publicKey": publicKey}

def aes_encrypt(key: bin, iv: bin, buffer: bin):
    """
    Encrypts the buffer using the key & iv (initialization vector) provided and then base64 encodes it.

    Parameters
    ----------
    key : bytes
        The key to use for encryption.
    iv : bytes
        The initialization vector to use for encryption.
    buffer : bytes
        The plaintext data to encrypt.

    Returns
    -------
    bytes
        The ciphertext resulting from the encryption of the plaintext.

    """
    # Pad the message using PKCS7 padding
    padder = PKCS7(algorithms.AES.block_size).padder()
    padded_buffer = padder.update(buffer) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    cipher_text = encryptor.update(padded_buffer) + encryptor.finalize()
    return base64.b64encode(cipher_text)

def aes_decrypt(key: bin, iv: bin, buffer: bin):
    """
    Decodes the base64 buffer and then decrypts it using the key & iv provided.

    Parameters
    ----------
    key : bytes
        The key to use for decryption.
    iv : bytes
        The initialization vector to use for decryption.
    buffer : bytes
        The base64-encoded ciphertext to decrypt.

    Returns
    -------
    str
        The plaintext resulting from the decryption of the ciphertext.

    """
    decoded = base64.b64decode(buffer)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    padded_text = decryptor.update(decoded) + decryptor.finalize()

    # Remove PKCS7 padding
    unpadder = PKCS7(algorithms.AES.block_size).unpadder()
    text = unpadder.update(padded_text) + unpadder.finalize()
    return text.decode()

def get_public_key_pem(public_key):
    """
    Convert the given public key object to a PEM-encoded string.

    Parameters
    ----------
    public_key : object
        The public key object to be converted to a PEM-encoded string.

    Returns
    -------
    str
        The PEM-encoded string representation of the public key object.
    """
    return public_key.public_bytes(encoding=Encoding.PEM, format=PublicFormat.SubjectPublicKeyInfo)

def create_base58_hash(inp):
    """
    Create a Base58-encoded hash from the given input data.

    Parameters
    ----------
    inp : bytes
        The input data to be hashed and encoded.

    Returns
    -------
    str
        The Base58-encoded hash of the input data.
    """
    bytes = sha256(inp).digest()
    base58_string = base58.b58encode(bytes)
    return base58_string

def calc_fingerprint(pem_binary):
    """
    Calculate the fingerprint of a given PEM-encoded binary.

    Parameters
    ----------
    pem_binary : bytes
        The binary data in PEM format to be hashed and encoded.

    Returns
    -------
    str
        The Base58-encoded hash of the input data in PEM format.
    """
    # Remove carriage returns before creating hash to bring into line with openSSL / volt format.
    pem_formatted = pem_binary.decode().replace("\r\n", "\n").encode("utf-8")
    return create_base58_hash(pem_formatted)

def load_public_key(public_keys_string):
    """
    Load a public key object from a given PEM-encoded string.

    Parameters
    ----------
    public_keys_string : str
        The PEM-encoded string representation of the public key object to be loaded.

    Returns
    -------
    object
        A public key object loaded from the given PEM-encoded string.
    """
    public_key_as_bytes = public_keys_string.encode('utf-8')
    return load_pem_public_key(public_key_as_bytes)

def load_x509_certificate(x509_certificate):
    """
    Load an X.509 certificate object from a given PEM-encoded string.

    Parameters
    ----------
    x509_certificate : str
        The PEM-encoded string representation of the X.509 certificate object to be loaded.

    Returns
    -------
    object
        An X.509 certificate object loaded from the given PEM-encoded string.
    """
    certDecoded = x509.load_pem_x509_certificate(
        str.encode(x509_certificate), default_backend()
    )
    return certDecoded

def signJWT(payload, issuer, private_key, algorithm_options = {}):
    """
    Sign a JSON Web Token (JWT) using the given payload, issuer, private key, and algorithm options.

    Parameters
    ----------
    payload : dict
        A dictionary containing the data to be included in the JWT.
    issuer : str
        A string representing the issuer of the JWT.
    private_key : object
        A private key object used to sign the JWT.
    algorithm_options : dict, optional
        A dictionary containing algorithm options for the signing process.
        The default algorithm is 'RS256' if not specified.
        Default is an empty dictionary.

    Returns
    -------
    str
        A string containing the signed JWT.

    Notes
    -----
    This function uses the `base64`, `json`, `cryptography.hazmat.primitives.asymmetric.padding`, and `cryptography.hazmat.primitives.hashes` modules.
    It is designed to be used with RSA-based private keys, and can sign JWTs with the RS256 algorithm by default.
    """
    header = {
        "alg": algorithm_options["algorithm"] if "algorithm" in algorithm_options else "RS256",
        "typ": "JWT",
        "kid": issuer,
    }

    stringified_header = json.dumps(header).encode('utf-8')
    stringified_payload = json.dumps(payload).encode('utf-8')

    # We need to use base64Url format for JWTs
    header_base64 = base64.urlsafe_b64encode(stringified_header).decode().replace("=", "")
    payload_base64 = base64.urlsafe_b64encode(stringified_payload).decode().replace("=", "")

    header_and_payload = f"{header_base64}.{payload_base64}"

    # Sign the hash with the private key
    signature = private_key.sign(header_and_payload.encode('utf-8'), padding.PKCS1v15(), hashes.SHA256())

    base64_signature = base64.urlsafe_b64encode(signature).decode().replace("=", "")
    return f"{header_and_payload}.{base64_signature}"

def aes_create_key():
    """
    Generate a new AES key and initialization vector.

    Returns
    -------
    dict
        A dictionary containing the generated key and initialization vector.

    Notes
    -----
    The generated key is a random 256-bit (32-byte) value, and the initialization vector
    is a random 128-bit (16-byte) value.
    """
    key = urandom(32)
    iv = urandom(16)
    return {"key": key, "iv": iv}

def rsa_encrypt(key, buffer):
    """
    Encrypt the buffer using the provided RSA key and return the encrypted text in base64 format.

    Parameters
    ----------
    key : cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey
        The RSA public key to be used for encryption.
    buffer : bytes
        The plaintext data to be encrypted.

    Returns
    -------
    str
        The encrypted data in base64-encoded format.

    Notes
    -----
    This function uses RSA encryption with OAEP padding and SHA-1 hashing.
    """
    cipher_text = key.encrypt(
        buffer,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA1()),
            algorithm=hashes.SHA1(),
            label=None
        )
    )
    return base64.b64encode(cipher_text).decode()

def rsa_decrypt(key, buffer):
    """
    Decrypt the base64-encoded buffer using the provided RSA key and return the plaintext.

    Parameters
    ----------
    key : cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey
        The RSA private key to be used for decryption.
    buffer : str
        The base64-encoded ciphertext data to be decrypted.

    Returns
    -------
    str
        The decrypted plaintext.

    Notes
    -----
    This function uses RSA decryption with OAEP padding and SHA-1 hashing.
    """
    decoded_buffer = base64.b64decode(buffer)
    plain_text = key.decrypt(
        decoded_buffer,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA1()),
            algorithm=hashes.SHA1(),
            label=None
        )
    )
    return plain_text.decode()

def get_identity_token(client_key_pair, target_key, target_audience, tunnelling = False, ttl = 60):
    """
    Generates an identity token as a JWT (JSON Web Token) that can be used to authenticate the client and authorize
    access to a specific service.

    Parameters
    ----------
    client_key_pair : dict
        A dictionary containing the client's public and private keys. Private key is used to sign the JWT, public key fingerprint
        embedded in the JWT payload, as the issuer.
    target_key : cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey
        The public key of the target service.
    target_audience : str
        The intended audience of the token.
    tunnelling : bool, optional
        A boolean flag indicating whether to use tunnelling, if true, adds a shared secret key & iv (initialisation vector) 
        to the payload which is encrypted with the target service's public key. Default is False.
    ttl : int, optional
        The time-to-live of the token in seconds. Default is 60.

    Returns
    -------
    dict
        A dictionary containing the token and any shared key details, if tunnelling is enabled.

    """
    pem_binary = get_public_key_pem(client_key_pair["publicKey"])
    base58Key = calc_fingerprint(pem_binary).decode()

    # Allow TTL either side of the current time
    # TODO: fix with server time sync on volt connection.

    timestamp = int(datetime.now().timestamp())
    payload = {
         "aud": target_audience,
         "iat": timestamp - ttl,
         "exp": timestamp + ttl,
    }

    shared_key = None
    if tunnelling:
        # Initialise the Relay encryption key.
        shared_key = aes_create_key()
        
        # Encrypt the key details using the target Volt public key and include this in the JWT payload.
        payload["sk"] = rsa_encrypt(target_key, shared_key["key"])
        payload["iv"] = rsa_encrypt(target_key, shared_key["iv"])

    # Sign synchronously.
    token = signJWT(payload, base58Key, client_key_pair["privateKey"])

    # Return the token along with any encryption key details.
    return {
         "token": token,
         "shared_key": shared_key,
    }