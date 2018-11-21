import logging
import auth
import json
import socket
import jwt
import argparse
import encrypt
import json
import pre
import chain
from gmssl import sm2

success_res = json.dumps({
    'status': '200',
    'msg': ''
})

error_res = lambda msg: json.dumps({
    'status': '401',
    'msg': msg
})

parser = argparse.ArgumentParser(description='chatroom server')
parser.add_argument('-p', metavar='PORT', type=int, default=51742,
help='UDP port (default 51742)')
args = parser.parse_args()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('127.0.0.1', args.p))

logging.info('crypto server established')

MAX_BYTES = 4096

clients = {}

while True:
    req_data, address = sock.recvfrom(MAX_BYTES)
    req_data = req_data.decode('ascii')
    logging.info('the server received {}'.format(req_data))
    j_parsed = json.loads(req_data)
    mode = j_parsed['mode']

    if mode == 'REGISTER':
        res_data = auth.register(j_parsed['username'], j_parsed['pubkey'])
    elif mode == 'LOGIN':
        res_data = auth.login(j_parsed['username'], 
            j_parsed['timeval'], j_parsed['signature'])
        if address not in clients.values():
            clients[j_parsed['username']] = address
    elif mode == 'TEST':
        res_data = success_res
    else:
        try: 
            claims = jwt.decode(j_parsed['jwt'].encode('ascii'), 
                auth.jwt_secret, algorithm='HS256')
        except:
            res_data = error_res('you have not logged in')
        else:
            file_progress = 'collecting {}: {}/{} bytes   % {:.2f}'
            if mode == 'UP':
                file_length = int(j_parsed['length'])
                file_name = j_parsed['name']
                file_data = b''
                res_data = json.dumps({
                    'status': '201',
                    'msg': 'ready'    
                })
                sock.sendto(res_data.encode('ascii'), address)
                logging.info('receiving file from {}:{}'.format(*address))

                # collect file fragments
                while len(file_data) < file_length:
                    # \x1b[2K\r
                    percent = 100 * len(file_data) / file_length
                    print(file_progress \
                        .format(file_name, len(file_data), file_length, percent))

                    file_frag, up_addr = sock.recvfrom(MAX_BYTES)
                    if address == up_addr:
                        file_data += file_frag
                print('\x1b[2K', end='\r')
                logging.info('{} received total length {} bytes' \
                    .format(file_name, file_length))

                # encrypt to .enc file
                enc_result = encrypt.encrypt(file_data)
                with open('documents/%s.enc' % file_name, 'wb') as f:
                    f.write(enc_result['enc'])

                # update database
                sql = """
                    INSERT INTO Files (Filename, Uploader, Pubkey, Pvtkey, length)
                    VALUES ('{}', '{}', '{}', '{}', '{}')
                """.format(file_name, claims['username'], 
                        enc_result['pubkey'], enc_result['pvtkey'], len(enc_result['enc']))
                pre.insert(sql)
                logging.info('database file list updated')
                res_data = success_res

            elif mode == 'DOWN':
                file_name = j_parsed['name']
                sql = "SELECT Pvtkey, Length FROM Files WHERE FileName='%s'" % file_name
                selected = pre.select(sql)[0]
                file_length = selected[1]

                # encrypt file-pvt key with user's pubkey
                sm2_crypt = sm2.CryptSM2(public_key=claims['pubkey'], private_key='')

                res_data = json.dumps({
                    'status': '200',
                    'enc_pvtkey': selected[0],
                    'length': file_length
                })
                sock.sendto(res_data.encode('ascii'), address)
                logging.info('the server sent {}'.format(res_data))

                # fragment and send files
                sent_len = 0
                with open('documents/%s.enc' % file_name, 'rb') as f:
                    while sent_len < file_length:
                        percent = 100 * sent_len / file_length
                        print(file_progress \
                            .format(file_name, sent_len, file_length, percent))
                        sock.sendto(f.read(MAX_BYTES), address) 
                        sent_len += MAX_BYTES
                logging.info('{} sent total length {} bytes' \
                    .format(file_name, file_length))
                res_data = success_res

            elif mode == 'FILELIST':
                sql = "SELECT DISTINCT FileName FROM Files"
                selected = pre.select(sql)
                res_data = json.dumps({
                    'status': '200',
                    'names': [item[0] for item in selected]    
                })

            elif mode == 'CHAIN':
                prev_visitor = j_parsed['pv']
                file_name = j_parsed['name']
                info = {
                    'time_stamp': eval(prev_visitor[0]), 
                    'signature': eval(prev_visitor[1]),
                    'ip_addr': eval(prev_visitor[2]),
                    'id': eval(prev_visitor[3])
                }
                chain.chain(info, 'documents/%s.enc' % file_name)
                res_data = success_res


            # if mode == 'PUBLIC':
            #     message = '{}[{}]: {}'.format(claims['username'], time_stamp, j_parsed['msg'])
            #     for user in clients:
            #         try:
            #             sock.sendto(json.dumps({
            #                 'status': '200',
            #                 'msg': message
            #             }).encode('ascii'), clients[user])
            #         except:
            #             del clients[user]
            #     res_data = json.dumps({
            #         'status': '200',
            #         'msg': ''
            #     })
            # elif mode == 'TO':
            #     message = '{}->{}[{}]: {}'.format(claims['username'], j_parsed['username'], time_stamp, j_parsed['msg'])
            #     try:
            #         sock.sendto(json.dumps({
            #             'status': '200',
            #             'msg': message
            #         }).encode('ascii'), clients[j_parsed['username']])
            #         res_data = json.dumps({
            #             'status': '200',
            #             'msg': message
            #         })
            #     except:
            #         del clients[user]
            #         res_data = json.dumps({
            #             'status': '404',
            #             'msg': 'target user offline'
            #         })


    sock.sendto(res_data.encode('ascii'), address)   
    logging.info('the server sent {}'.format(res_data))


