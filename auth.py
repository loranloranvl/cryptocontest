import json
import jwt
import time
import logging
import pre
from gmssl import sm2
jwt_secret = 'tuna and bacon are my favorite'

def register(username, pubkey):
    # ensure user names are distinct
    sql = "SELECT * FROM Users WHERE UserName='{}'".format(username)
    if len(pre.select(sql)) != 0:
        return json.dumps({
            'status': '401',
            'msg': 'user name duplicated'
        })

    # store usename and hashed password into the database
    sql = "INSERT INTO Users (UserName, Pubkey) VALUES ('{}', '{}')".format(username, pubkey)
    pre.insert(sql)
    logging.info('{} registered with pubkey {}'.format(username, pubkey))
    return json.dumps({
        'status': '200',
        'msg': 'successfully registered'
    })

def login(username, timeval, signature):
    # verify username
    sql = "SELECT * FROM Users WHERE UserName='{}'".format(username)
    selected = pre.select(sql)
    if len(selected) == 0:
        return json.dumps({
            'status': '401',
            'msg': 'user name not exists'    
        })

    # verify signature
    pubkey = selected[0][1]
    sm2_verify = sm2.CryptSM2(public_key=pubkey, private_key='')
    if not sm2_verify.verify(signature, (username + timeval).encode('ascii')):
        return json.dumps({
            'status': '401',
            'msg': 'wrong keys'
        })

    logging.info('{} logged in'.format(username))
    claims = {
        'username': username,
        'pubkey': pubkey
    }
    
    jwt_encoded = jwt.encode(claims, jwt_secret, algorithm='HS256')
    return json.dumps({
        'status': '200',
        'msg': 'successfully logged in',
        'jwt': str(jwt_encoded)[1:].strip('\'')
    })