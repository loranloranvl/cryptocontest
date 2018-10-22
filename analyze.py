import sys
import time
from gmssl.sm4 import CryptSM4, SM4_ENCRYPT, SM4_DECRYPT
from gmssl import sm2, sm3, func

file_path = sys.argv[1]
print('analyzing', file_path)
with open(file_path, 'rb') as file:
    file_enc = file.read()
    print('total {} bytes'.format(len(file_enc)))

data, end_file = func.destructure(file_enc)
visited = data['flags'][0] >= 8 * 16
print('visited', visited)
for key in data:
    item = data[key]
    if len(item) > 32:
        print(key, 'of length', len(item))
    elif len(item) > 6:
        print('{} {}... of length {}'.format(key, item[0:6].hex(), len(item)))
    else:
        print(key, int.from_bytes(data[key], 'big'))

print()
for i in range(end_file + 32, len(file_enc), 110):
    info = func.parse_info(file_enc[i:i + 78])
    if i == end_file + 32:
        person_str, role_str = 'creator', 'public key'
    else:
        person_str, role_str = 'visitor', 'signature'
    ip_str = '.'.join([str((info['ip_addr'] >> i) % 256) for i in range(0, 32, 8)][::-1])
    time_str = time.asctime(time.localtime(info['time_stamp']))
    print('{} {} at {}'.format(person_str, ip_str, time_str))
    print('{} beginning with {}'.format(role_str, info['signature'][0:4].upper()))