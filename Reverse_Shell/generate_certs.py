"""
Generate SSL/TLS certificates for the reverse shell.
Uses openssl to create a self-signed cert + private key.

Usage: python generate_certs.py
"""

import subprocess
import os
import sys


CERTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "certs")
KEY_FILE = os.path.join(CERTS_DIR, "server.key")
CERT_FILE = os.path.join(CERTS_DIR, "server.crt")
KEY_BITS = 2048
CERT_DAYS = 365


def check_openssl():
    try:
        result = subprocess.run(["openssl", "version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[+] Found: {result.stdout.strip()}")
            return True
        print("[-] openssl found but returned an error")
        return False
    except FileNotFoundError:
        print("[-] openssl is not installed or not in PATH")
        print("    Windows: install Git for Windows (includes openssl)")
        print("    Linux:   sudo apt install openssl")
        print("    macOS:   brew install openssl")
        return False


