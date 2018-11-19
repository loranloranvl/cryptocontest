import math
import time
import socket
import sys
import ecckeygen
import random
import string
from gmssl.sm4 import CryptSM4, SM4_ENCRYPT, SM4_DECRYPT
from gmssl import sm2, sm3, func

def encrypt(file_data):
    endianness = func.endianness

    data = {
        'flags': b'', # visited ... | size 1 byte
        'sm4_key_len': b'', # length of the next shit | size 1 byte
        'sm4_key': b'', # encrypted sm4 key
        'file_len': b'', # length of the next shit | size 4 bytes
        'file_encrypted': b'',
        'digest0': b'', # digest of all above | size 32 bytes
        'init_info': b'',
        'digest1': b'' # digest of digest0 + init_info | size 32 bytes
    }
    endianness = 'big'
    data['flags'] = bytes.fromhex('00')

    keys = ecckeygen.generate()
    public_key = keys['pubkey']
    sm4_key = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16)).encode('ascii')
    assert len(public_key) == 128 and len(sm4_key) == 16

    # encrypt sm4_key with sm2
    sm2_crypt = sm2.CryptSM2(public_key=public_key, private_key='')
    data['sm4_key'] = sm2_crypt.encrypt(sm4_key)
    data['sm4_key_len'] = len(data['sm4_key']).to_bytes(1, endianness)

    # encrypt file with sm4
    sm4_crypt = CryptSM4()
    sm4_crypt.set_key(sm4_key, SM4_ENCRYPT)
    data['file_encrypted'] = sm4_crypt.crypt_ecb(file_data)
    file_len = len(data['file_encrypted'])
    # the block length of sm4 is 16 bytes
    block_len = 16
    assert file_len % block_len == 0 and \
           file_len / block_len == math.ceil(len(file_data) / block_len)

    # 4 bytes = 32 bits is able to represent 2 ** 32 * block_len, which is 64GB
    data['file_len'] = file_len.to_bytes(4, endianness)

    # sm3 digest of all above
    file1 = data['file_len'] + data['sm4_key'] + data['file_encrypted']
    data['digest0'] = sm3.hash(file1)
    assert len(data['digest0']) == 32

    # initial information
    ip_addr = socket.gethostbyname(socket.gethostname())
    creator_id = 0
    init_info = {
        'time_stamp': int(time.time()).to_bytes(4, endianness),
        'public_key': bytes.fromhex(public_key),
        'ip_addr': b''.join([int(i).to_bytes(1, endianness) for i in ip_addr.split('.')]),
        'id': creator_id.to_bytes(6, endianness)
    }
    data['init_info'] = func.cat_bytes(init_info)
    assert len(data['init_info']) == 4 + 64 + 4 + 6

    # digest of digest0 + init_info
    data['digest1'] = sm3.hash(data['digest0'] + data['init_info'])

    # output
    return {
        'enc': func.cat_bytes(data),
        **keys
    }
