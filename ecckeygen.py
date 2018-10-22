import csv
from gmssl import sm2, func

with open('database/keypairs.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    for i in range(100):
        private_key = func.random_hex(66)
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

        print('private_key = ' + repr(private_key))
        print('public_key = ' + repr(public_key))
        print()

        writer.writerow([func.random_hex(12), private_key, public_key])
    


