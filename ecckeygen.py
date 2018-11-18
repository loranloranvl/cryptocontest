from gmssl import sm2, func

def generate():
    private_key = '00' + func.random_hex(64)
    # private_key = '00B9AB0B828FF68872F21A837FC303668428DEA11DCD1B24429D0C99E24EED83D5'
    public_key = ''
    sm2_crypt = sm2.CryptSM2(public_key=public_key, private_key=private_key)
    # public_key(point) = private_key(int) * g(generator point)
    public_key = sm2_crypt._kg2(int(private_key, 16), sm2.default_ecc_table['g'])
    # ensure that works
    sm2_crypt = sm2.CryptSM2(public_key=public_key, private_key=private_key)

    data = b'zeox'
    enc_data = sm2_crypt.encrypt(data)
    dec_data =sm2_crypt.decrypt(enc_data)
    assert dec_data == data, 'generation failed, try again'

    random_hex_str = func.random_hex(sm2_crypt.para_len)
    sign = sm2_crypt.sign(data, random_hex_str)
    assert sm2_crypt.verify(sign, data)

    return {
        'pubkey': public_key,
        'pvtkey': private_key
    }