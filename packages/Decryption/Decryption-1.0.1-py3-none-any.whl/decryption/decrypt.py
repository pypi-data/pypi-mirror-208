
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Protocol.KDF import PBKDF2
import base64
import json
import re


def decrypt(encrypted_data,password,salt,IV):
    try:
        decoded_value = base64.b64decode(encrypted_data)
        key = PBKDF2(password, salt, 16, 65536)
        cipher = AES.new(key, AES.MODE_CBC,IV)
        dec_value = cipher.decrypt(decoded_value)
        decrypted_data =  dec_value.decode('utf-8')
        result = re.search(r'{(.+?)}', decrypted_data).group(0)
        result = json.loads(result)   
        return result
    except Exception as e:
        raise ValueError("Invalid Input")


