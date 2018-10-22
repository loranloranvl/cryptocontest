import math
import time
import socket
import sys
from uuid import getnode
from gmssl.sm4 import CryptSM4, SM4_ENCRYPT, SM4_DECRYPT
from gmssl import sm2, sm3, func

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

private_key = ''
public_key = 'B9C9A6E04E9C91F7BA880429273747D7EF5DDEB0BB2FF6317EB00BEF331A83081A6994B8993F3F5D6EADDDB81872266C87C018FB4162F5AF347B483E24620207'
sm4_key = b'3l5butlj26hvv313'
assert len(public_key) == 128 and len(sm4_key) == 16

# encrypt sm4_key with sm2
sm2_crypt = sm2.CryptSM2(public_key=public_key, private_key=private_key)
data['sm4_key'] = sm2_crypt.encrypt(sm4_key)
data['sm4_key_len'] = len(data['sm4_key']).to_bytes(1, endianness)

file_path = sys.argv[1]
print('encrypting', file_path)
file_data = None
with open(file_path, 'rb') as file:
    file_data = file.read()
    assert len(file_data) < 2 ** 30

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
with open(file_path + '.enc', 'wb') as file:
    file.write(func.cat_bytes(data))
