import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from os import getenv


class Cryptology:
    '''
    Encryotar y desemcriptar mensajes de Kafka
    '''

    # Variables de clase

    def __init__(self, pad: int = None):
        # Padding
        self.PAD = pad
        self.key = getenv('JWT_SECRET')  # Must Be 16 char for AES128

    def encrypt(self, raw):
        raw = pad(raw.encode(), self.PAD)
        cipher = AES.new(self.key.encode('utf-8'), AES.MODE_ECB)
        return base64.b64encode(cipher.encrypt(raw)).decode('utf-8', 'ignore')

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        cipher = AES.new(self.key.encode('utf-8'), AES.MODE_ECB)
        return unpad(cipher.decrypt(enc), self.PAD).decode('utf-8', 'ignore')
