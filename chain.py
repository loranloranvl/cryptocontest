import time
import sys
import csv
from gmssl.sm4 import CryptSM4, SM4_ENCRYPT, SM4_DECRYPT
from gmssl import sm2, sm3, func

# require info from the client
# info length: 4 + 64 + 4 + 6
with open('database/visitors.csv') as file:
    prev_visitor = list(csv.reader(file))[-1]

info = {
    'time_stamp': eval(prev_visitor[0]), 
    'signature': eval(prev_visitor[1]),
    'ip_addr': eval(prev_visitor[2]),
    'id': eval(prev_visitor[3])
}

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
