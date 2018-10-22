import math
import time
import socket
import csv
from random import randint
from uuid import getnode
from gmssl.sm4 import CryptSM4, SM4_ENCRYPT, SM4_DECRYPT
from gmssl import sm2, sm3, func

endianness = func.endianness

file_path = sys.argv[1]
print('decrypting', file_path)
with open(file_path, 'rb') as file:
    file_enc = file.read()
    assert len(file_enc) < 2 ** 30

data = func.destructure(file_enc)[0]

# decrypt sm4 key
private_key = '00B9AB0B828FF68872F21A837FC303668428DEA11DCD1B24429D0C99E24EED83D5'
public_key = 'B9C9A6E04E9C91F7BA880429273747D7EF5DDEB0BB2FF6317EB00BEF331A83081A6994B8993F3F5D6EADDDB81872266C87C018FB4162F5AF347B483E24620207'
sm2_crypt = sm2.CryptSM2(public_key=public_key, private_key=private_key)
sm4_key = sm2_crypt.decrypt(data['sm4_key'])

# verify digestn
lf = len(file_enc)
if sm3.hash(file_enc[lf - 142:lf - 32]) != file_enc[lf - 32:].hex():
    raise Exception('block digest unmatch')
    # clear buffer and request again
    pass
else:
    visited = data['flags'][0] >= 8 * 16
    if visited:
        info = func.parse_info(file_enc[lf - 110:lf - 32])
        prev_signature = info['signature']

        # verify the previous visitor's signature
        # this shall be done by the server
        # but here we use local csv file for demonstration
        with open('database/keypairs.csv') as file:
            kps = csv.reader(file)
            for kp in kps:
                
    # decypt file
    # crypt_sm4 = CryptSM4()
    # crypt_sm4.set_key(sm4_key, SM4_DECRYPT)
    # file_data = crypt_sm4.crypt_ecb(data['file_encrypted'])
    # with open('123.pdf', 'wb') as file:
    #   file.write(file_data)

    # update the visitor's chain
    # post the info dict ↓ to the server
    sign_key = '0ea157aedb10bd2ae2d651b89f268f48c889f11272710332eaf76a15fc2d1babed'
    sm2_sign = sm2.CryptSM2(public_key='', private_key=sign_key)
    random_hex_str = func.random_hex(sm2_sign.para_len)
    print(sm2_sign.sign(init_block, random_hex_str))
    ip_addr = socket.gethostbyname(socket.gethostname())
    info = {
        'time_stamp': int(time.time()).to_bytes(4, endianness),
        'signature': bytes.fromhex(sm2_sign.sign(init_block, random_hex_str)),
        'ip_addr': b''.join([int(i).to_bytes(1, endianness) for i in ip_addr.split('.')]),
        'mac_addr': getnode().to_bytes(6, endianness)
    }
    print(repr(info))
