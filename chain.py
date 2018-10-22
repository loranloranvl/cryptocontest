import time
import sys
from gmssl.sm4 import CryptSM4, SM4_ENCRYPT, SM4_DECRYPT
from gmssl import sm2, sm3, func

# require info from the client
# info length: 4 + 64 + 4 + 6
info = {'time_stamp': b'[\xcb\x05\xcc', 'ip_addr': b'\xc0\xa8\x00h', 'id': b'(\xc2\xddk\x0fb', 'signature': b'\x0fvRT\xe28\xa4\xe6\x02\xbed\x03R\xb3\xae\xd3nt/\xb8\xe8\xa2N)\x07\xbe\xa06\x08\xf6\xc9\x0e\x8fCg\x81Dx\xc7\x1c\x8c\xb9\xad\x99\xf9\xda\xf6\x83yPX\x8aM\xc3\x92%\xe9\xef3\x80\xbd\x01\x16\xfb'}

file_path = sys.argv[1]
print('chaining', file_path)
with open(file_path, 'rb') as file:
    file_enc = file.read()
    assert len(file_enc) < 2 ** 30

data = func.destructure(file_enc)[0]
file_new = b''

stream = func.cat_bytes(info)
last_block = file_enc[len(file_enc) - 32:] + stream

# set the first bit of flags(visited) to 1
file_new = ((1 << 7) + file_enc[0] % (1 << 7)).to_bytes(1, func.endianness) + \
           file_enc[1:] + stream + sm3.hash(last_block)

with open(file_path, 'wb') as file:
    file.write(file_new)
