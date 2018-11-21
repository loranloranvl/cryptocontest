from random import choice


xor = lambda a, b:list(map(lambda x, y: x ^ y, a, b))

rotl = lambda x, n:((x << n) & 0xffffffff) | ((x >> (32 - n)) & 0xffffffff)

get_uint32_be = lambda key_data:((key_data[0] << 24) | (key_data[1] << 16) | (key_data[2] << 8) | (key_data[3]))

put_uint32_be = lambda n:[((n>>24)&0xff), ((n>>16)&0xff), ((n>>8)&0xff), ((n)&0xff)]

padding = lambda data, block=16: data + [(16 - len(data) % block)for _ in range(16 - len(data) % block)]

unpadding = lambda data: data[:-data[-1]]

list_to_bytes = lambda data: b''.join([bytes((i,)) for i in data])

bytes_to_list = lambda data: [i for i in data]

random_hex = lambda x: ''.join([choice('0123456789abcdef') for _ in range(x)])

str_to_list = lambda data: [bytes(i, encoding="ascii")[0] for i in data]

endianness = 'big'
def destructure(file_data):
    data = {
        'flags': b'',
        'sm4_key_len': b'',
        'sm4_key': b'',
        'file_len': b'',
        'file_encrypted': b'',
        'digest0': b'',
        'init_info': b'',
        'digest1': b''
    }
    data['flags'] = file_data[0:1]
    data['sm4_key_len'] = file_data[1:2]
    end_key = 2 + int.from_bytes(data['sm4_key_len'], endianness)
    data['sm4_key'] = file_data[2:end_key]
    data['file_len'] = file_data[end_key:end_key + 4]
    end_file = end_key + 4 + int.from_bytes(data['file_len'], endianness)
    data['file_encrypted'] = file_data[end_key + 4:end_file]
    data['digest0'] = file_data[end_file:end_file + 32]
    data['init_info'] = file_data[end_file + 32:end_file + 32 + 4 + 64 + 4 + 6]
    data['digest1'] = file_data[end_file + 110:end_file + 142]

    return (data, end_file)

def cat_bytes(bytes_dict):
    stream = b''
    for key in bytes_dict:
        stream += bytes_dict[key]
        print(key, len(bytes_dict[key]))
    return stream

def parse_info(info_):
    return {
        'time_stamp': int.from_bytes(info_[0:4], endianness),
        'signature': info_[4:68].hex(),
        'ip_addr': int.from_bytes(info_[68:72], endianness),
        # 'id': int.from_bytes(info_[72:78], endianness)
        'id': info_[72:78].decode('ascii')
    }
