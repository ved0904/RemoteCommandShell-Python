"""
AES-256 encryption module for secure communication.
"""

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import hashlib

BLOCK_SIZE = 16


def get_key(secret):
    if isinstance(secret, str):
        secret = secret.encode('utf-8')
    return hashlib.sha256(secret).digest()


def pad(data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    padding_len = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
    return data + bytes([padding_len] * padding_len)


def unpad(data):
    padding_len = data[-1]
    return data[:-padding_len]


def encrypt(plaintext, key):
    if isinstance(plaintext, str):
        plaintext = plaintext.encode('utf-8')
    
    key = get_key(key)
    iv = get_random_bytes(BLOCK_SIZE)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    padded = pad(plaintext)
    ciphertext = cipher.encrypt(padded)
    
    return iv + ciphertext


def decrypt(ciphertext, key):
    if len(ciphertext) < BLOCK_SIZE:
        raise ValueError("Ciphertext too short")
    
    key = get_key(key)
    iv = ciphertext[:BLOCK_SIZE]
    encrypted = ciphertext[BLOCK_SIZE:]
    
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(encrypted)
    
    return unpad(decrypted)


def send_encrypted(sock, data, key):
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    encrypted = encrypt(data, key)
    length = len(encrypted)
    sock.send(length.to_bytes(4, 'big') + encrypted)


def recv_encrypted(sock, key):
    length_bytes = sock.recv(4)
    if not length_bytes:
        return None
    
    length = int.from_bytes(length_bytes, 'big')
    
    encrypted = b''
    while len(encrypted) < length:
        chunk = sock.recv(min(4096, length - len(encrypted)))
        if not chunk:
            break
        encrypted += chunk
    
    return decrypt(encrypted, key)
