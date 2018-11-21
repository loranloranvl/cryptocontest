import sys
import math
import time
import socket
import csv
import random
import re
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QTextEdit,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QFileDialog,
    QLineEdit
)
from PyQt5.QtGui import QIcon, QFont
from gmssl.sm4 import CryptSM4, SM4_ENCRYPT, SM4_DECRYPT
from gmssl import sm2, sm3, func
import viewer

def decrypt(info_raw, file_enc):
    endianness = func.endianness

    data = func.destructure(file_enc)[0]

    # decrypt sm4 key
    private_key = info_raw['decrypt key']
    public_key = ''
    sm2_crypt = sm2.CryptSM2(public_key=public_key, private_key=private_key)
    sm4_key = sm2_crypt.decrypt(data['sm4_key'])

    # verify digestn
    lf = len(file_enc)
    # if sm3.hash(file_enc[lf - 142:lf - 32]) != file_enc[lf - 32:]:
    #     return 'block digest unmatch'

    visited = data['flags'][0] >= 8 * 16
    prev_info = func.parse_info(file_enc[lf - 110:lf - 32])
    if visited:
        prev_signature = prev_info['signature']
        prev_id = prev_info['id']
        prev_pubkey = None

        # verify the previous visitor's signature
        # this shall be done by the server
        # but here we use local csv file for demonstration
        # with open('database/keypairs.csv') as file:
        #     kps = csv.reader(file)
        #     for kp in kps:
        #         if kp[0] == prev_id:
        #             prev_pubkey = kp[2]
        #             break

        # assert prev_pubkey != None, 'signer not found'

        # sm2_verify = sm2.CryptSM2(public_key=prev_pubkey, private_key='')
        # prev_sign_data = file_enc[lf - 110:lf - 106] + file_enc[lf - 42:lf - 32]
        # assert sm2_verify.verify(prev_signature, prev_sign_data)

    ip_addr = socket.gethostbyname(socket.gethostname())
    my_info = {
        'time_stamp': int(time.time()).to_bytes(4, endianness),
        'signature': b'',
        'ip_addr': b''.join([int(i).to_bytes(1, endianness) for i in ip_addr.split('.')]),
        'id': info_raw['id'].encode('ascii')
    }
    sm2_sign = sm2.CryptSM2(public_key='', private_key=info_raw['private key'])
    random_hex_str = func.random_hex(sm2_crypt.para_len)
    sign_data = my_info['time_stamp'] + my_info['ip_addr'] + my_info['id']
    my_info['signature'] = bytes.fromhex(sm2_sign.sign(sign_data, random_hex_str))
                
    # decypt file
    crypt_sm4 = CryptSM4()
    crypt_sm4.set_key(sm4_key, SM4_DECRYPT)
    file_data = crypt_sm4.crypt_ecb(data['file_encrypted'])

    # update the visitor's chain
    # post the my_info dict to the server
    # with open('database/visitors.csv', 'w', newline='') as file:
    #     writer = csv.writer(file)
    #     writer.writerow([repr(my_info[key]) for key in my_info])

    try:
        viewer.viewPdfBytes(file_data)
    except RuntimeError:
        return 'wrong decrypt key'
    return [repr(my_info[key]) for key in my_info]
        

# class QtGui(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.initUI()

#     def initUI(self):
#         self.structureLabel = QLabel('Enc-File Decrypter')
#         self.structureLabel.setStyleSheet('''
#             color: #333;
#             font-size: 35px;
#             font-weight: 700;
#             margin-top: 10px;
#             margin-bottom: 35px;
#         ''')

#         self.idLabel = QLabel('user ID    ')
#         # self.pubkeyLabel = QLabel('public key ')
#         self.pvtkeyLabel = QLabel('private key')
#         self.deckeyLabel = QLabel('decrypt key')

#         for item in [self.idLabel, self.pvtkeyLabel, self.deckeyLabel]:
#             item.setStyleSheet('''
#                 width: 200px;
#                 color: #333;
#                 font-size: 25px;
#                 font-weight: 400;
#             ''')

#         self.idEdit = QLineEdit()
#         # self.pubkeyEdit = QLineEdit()
#         self.pvtkeyEdit = QLineEdit()
#         self.deckeyEdit = QLineEdit()

#         for item in [self.idEdit, self.pvtkeyEdit, self.deckeyEdit]:
#             item.setStyleSheet('''
#                 padding: 5px 8px;
#                 width: 600px;
#                 font-size: 22px;
#                 color: #333;
#                 margin-left: 10px;
#             ''')

#         self.fileBtn = QPushButton('Select File', self)
#         self.fileBtn.clicked.connect(self.openFile)
#         self.fileBtn.setStyleSheet('''
#             background-color: #80aaff;
#             color: white;
#             margin: 25px;
#             width: 140px;
#             height: 30px;
#             padding: 10px 24px;
#             border: none;
#             font-weight: 1000;
#             font-size: 22px;
#         ''')

#         self.msgLabel = QLabel('')
#         self.msgLabel.setStyleSheet('''
#             color: #ff6666;
#             font-size: 26px;
#             font-weight: 500;
#         ''')

#         labelHbox = QHBoxLayout()
#         labelHbox.addStretch(1)
#         labelHbox.addWidget(self.structureLabel)
#         labelHbox.addStretch(1)

#         idHbox = QHBoxLayout()
#         idHbox.addStretch(1)
#         idHbox.addWidget(self.idLabel)
#         idHbox.addWidget(self.idEdit)
#         idHbox.addStretch(1)

#         # pubkeyHbox = QHBoxLayout()
#         # pubkeyHbox.addStretch(1)
#         # pubkeyHbox.addWidget(self.pubkeyLabel)
#         # pubkeyHbox.addWidget(self.pubkeyEdit)
#         # pubkeyHbox.addStretch(1)

#         pvtkeyHbox = QHBoxLayout()
#         pvtkeyHbox.addStretch(1)
#         pvtkeyHbox.addWidget(self.pvtkeyLabel)
#         pvtkeyHbox.addWidget(self.pvtkeyEdit)
#         pvtkeyHbox.addStretch(1)

#         deckeyHbox = QHBoxLayout()
#         deckeyHbox.addStretch(1)
#         deckeyHbox.addWidget(self.deckeyLabel)
#         deckeyHbox.addWidget(self.deckeyEdit)
#         deckeyHbox.addStretch(1)

#         btnHbox = QHBoxLayout()
#         btnHbox.addStretch(1)
#         btnHbox.addWidget(self.fileBtn)
#         btnHbox.addStretch(1)

#         msgHbox = QHBoxLayout()
#         msgHbox.addStretch(1)
#         msgHbox.addWidget(self.msgLabel)
#         msgHbox.addStretch(1)

#         vbox = QVBoxLayout()
#         vbox.addStretch(1)
#         vbox.addLayout(labelHbox)
#         vbox.addLayout(idHbox)
#         # vbox.addLayout(pubkeyHbox)
#         vbox.addLayout(pvtkeyHbox)
#         vbox.addLayout(deckeyHbox)
#         vbox.addLayout(btnHbox)
#         vbox.addLayout(msgHbox)
#         vbox.addStretch(1)

#         self.setLayout(vbox)

#         self.step = 0

#         self.setGeometry(500, 250, 900, 500)
#         self.setWindowTitle('D3CRYPT decrypter')
#         self.setWindowIcon(QIcon('img/key.png'))
#         self.setStyleSheet("background-color: white;")

#         self.show()

#     def showMsg(self, content):
#         self.msgLabel.setText(content)

#     def openFile(self):
#         info_raw = {
#             'id': self.idEdit.text(),
#             # 'public key': self.pubkeyEdit.text(),
#             'private key': self.pvtkeyEdit.text(),
#             'decrypt key': self.deckeyEdit.text()
#         }
#         for key in info_raw:
#             if len(info_raw[key]) == 0:
#                 self.showMsg(key + ' cannot be empty')
#                 return
#             try:
#                 int(info_raw[key], 16)
#             except ValueError:
#                 self.showMsg(key + ' is invalid')
#                 return
#             self.showMsg('')

#         fname = QFileDialog.getOpenFileName(self, 'Open file', r'D:\\projects\\cryptocontest\\project')
#         if fname[0]:
#             if '.enc' not in fname[0]:
#                 self.showMsg('invalid document\nyou should select a .enc file')
#                 return
#             self.showMsg('')
#             self.showMsg(main(info_raw, fname[0]))

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     gui = QtGui()

#     sys.exit(app.exec_())