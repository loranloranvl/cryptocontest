import socket
import json
import logging
import time
import sys
import ecckeygen
import os
from gmssl import func, sm2
import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg
from PyQt5.QtCore import Qt

MAX_BYTES = 4096
jwt = None
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect(('127.0.0.1', 51742))

# print(sock.recvfrom(4096))

def layoutCenter(box, *items):
    box.addStretch(1)
    for item in items:
        if repr(type(item)) == "<class 'PyQt5.QtWidgets.QLabel'>":
            box.addWidget(item)
        if repr(type(item)) == "<class 'PyQt5.QtWidgets.QHBoxLayout'>":
            box.addLayout(item)
    box.addStretch(1)

class QtGui(qw.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        width = 1200
        height = width / 1.618
        self.setGeometry(300, 90, width, height)
        self.setWindowTitle('D3CRYPT')
        self.setWindowIcon(qg.QIcon('img/key.png'))
        self.setStyleSheet("background-color: white;")

        qtRectangle = self.frameGeometry()
        centerPoint = qw.QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self.show()

class QtGui2(qw.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.logo = qw.QLabel()
        self.logo.setPixmap(qg.QPixmap("img/logo.png"))
        logoHbox = qw.QHBoxLayout()
        layoutCenter(logoHbox, self.logo)

        self.registerBtn = qw.QPushButton('Register')
        self.registerBtn.clicked.connect(self.handleRegister)
        self.loginBtn = qw.QPushButton('Login')
        self.loginBtn.clicked.connect(self.handleLogin)
        for btn in [self.registerBtn, self.loginBtn]:
            btn.setCursor(qg.QCursor(Qt.PointingHandCursor))
            btn.setStyleSheet('''
                QPushButton {
                    background-color: white;
                    color: #666;
                    margin: 15px;
                    padding: 10px 24px;
                    border: none;
                    font-weight: 1000;
                    font-size: 60px;
                    font-family: fort;
                }
                QPushButton:hover {
                    color: #111;
                }
            ''')

        btnHbox = qw.QHBoxLayout()
        btnHbox.addStretch(2)
        btnHbox.addWidget(self.registerBtn)
        btnHbox.addStretch(1)
        btnHbox.addWidget(self.loginBtn)
        btnHbox.addStretch(2)

        self.statuses = []
        for i in range(3):
            icon = qw.QLabel()
            icon.setPixmap(qg.QPixmap("img/blank.png"))
            text = qw.QLabel('')
            text.setStyleSheet('''
                color: #666;
                font-size: 32px;
            ''')
            hbox = qw.QHBoxLayout()
            layoutCenter(hbox, icon, text)
            self.statuses.append((hbox, icon, text))

        vbox = qw.QVBoxLayout()
        vbox.addStretch(3)
        vbox.addLayout(logoHbox)
        vbox.addStretch(1)
        vbox.addLayout(btnHbox)
        vbox.addStretch(1)
        for status in self.statuses:
            vbox.addLayout(status[0])
        vbox.addStretch(2)

        self.setLayout(vbox)

        # window basics
        width = 1200
        height = width / 1.618
        self.setGeometry(300, 90, width, height)
        self.setWindowTitle('D3CRYPT')
        self.setWindowIcon(qg.QIcon('img/key.png'))
        self.setStyleSheet("background-color: white;")

        # center align
        qtRectangle = self.frameGeometry()
        centerPoint = qw.QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self.show()

    # def handleRegister(self, e):
    #     self.dialog = qw.QDialog()
    #     self.dialog.setStyleSheet("background-color: white;")
    #     self.dialog.setWindowIcon(qg.QIcon('img/query.png'))
    #     self.dialog.setWindowTitle('User Name Input')

    #     label = qw.QLabel("Enter your user name")
    #     label.setStyleSheet('''
    #         color: #333;
    #         font-size: 26px;
    #     ''')

    #     self.usernameInput = qw.QLineEdit()
    #     self.usernameInput.setStyleSheet('''
    #         padding: 5px 8px;
    #         font-size: 22px;
    #         color: #333;
    #         margin-left: 10px;
    #         text-align: center;
    #     ''')

    #     btn = qw.QPushButton("Submit", self)
    #     btn.setStyleSheet('''
    #         background-color: #80aaff;
    #         color: white;
    #         margin: 25px;
    #         width: 140px;
    #         height: 30px;
    #         padding: 10px 24px;
    #         border: none;
    #         font-weight: 1000;
    #         font-size: 22px;
    #     ''')

    #     labelHbox = qw.QHBoxLayout()
    #     layoutCenter(labelHbox, label)

    #     inputHbox = qw.QHBoxLayout()
    #     layoutCenter(inputHbox, self.usernameInput)

    #     btnHbox = qw.QHBoxLayout()
    #     layoutCenter(btnHbox, btn)

    #     vbox = qw.QVBoxLayout()
    #     vbox.addStretch(1)
    #     vbox.addLayout(labelHbox)
    #     vbox.addLayout(inputHbox)
    #     vbox.addLayout(btnHbox)
    #     # for widget in [label, self.usernameInput, btn]:
    #     #     hbox = qw.QHBoxLayout()
    #     #     layoutCenter(hbox, widget)
    #     #     vbox.addLayout(hbox)
    #     vbox.addStretch(1)
    #     self.dialog.setLayout(vbox)

    #     width = 400
    #     height = width / 1.618
    #     self.dialog.setGeometry(720, 420, width, height)
    #     self.dialog.exec_()

    def handleRegister(self, e):
        self.clearStatuses()
        username, ok = qw.QInputDialog.getText(self, 'name', 
                   'Enter your name:')
        if ok:
            keys = ecckeygen.generate()
            self.changeStatus(0, 'sm2 key-pair generated', 'check')

            self.changeStatus(1, 'posting public key', 'loader')
            req_data = json.dumps({
                'mode': 'REGISTER',
                'username': username,
                'pubkey': keys['pubkey']
            })
            sock.send(req_data.encode('ascii'))
            res = sock.recv(MAX_BYTES).decode('ascii')
            res_data = json.loads(res)
            if res_data['status'] == '200':
                self.changeStatus(1, 'public key posted', 'check')
                self.changeStatus(2, 'successfully registed', 'check')
                with open('%s_keys.json' % username, 'w') as f:
                    f.write(json.dumps({
                        'username': username,
                        **keys
                    }))
            else:
                self.changeStatus(1, res_data['msg'], 'wrong')

    def handleLogin(self, e):
        global jwt
        self.clearStatuses()
        username, ok = qw.QInputDialog.getText(self, 'name', 
                   'Enter your name:')
        if not ok:
            return

        keys = None
        self.changeStatus(0, 'searching local keys', 'loading')
        # time.sleep(500)
        found = False
        for filename in os.listdir('.'):
            if filename == "%s_keys.json" % username:
                found = True
                with open(filename, 'r') as f:
                    keys = json.loads(f.read())
        if not found:
            self.changeStatus(0, 'keys.json not found', 'question')
            self.changeStatus(1, 'please select it yourself', 'question')
            # time.sleep(500)
            fname = qw.QFileDialog.getOpenFileName(self, 'select keys.json', '.')
            if fname[0] and filename == ("%s_keys.json" % username):
                with open(fname[0], 'r') as f:
                    keys = json.loads(f.read())
            else:
                self.changeStatus(0, 'that is not your key', 'wrong')
                return
        self.clearStatuses()

        self.changeStatus(0, 'posting signature', 'loader')
        timestring = str(int(time.time()))
        sm2_sign = sm2.CryptSM2(public_key='', private_key=keys['pvtkey'])
        random_hex_str = func.random_hex(sm2_sign.para_len)
        sign_data = (username + timestring).encode('ascii')
        req_data = json.dumps({
            'mode': 'LOGIN',
            'username': username,
            'timeval': timestring,
            'signature': sm2_sign.sign(sign_data, random_hex_str)
        })
        sock.send(req_data.encode('ascii'))
        res = sock.recv(MAX_BYTES).decode('ascii')
        res_data = json.loads(res)
        if res_data['status'] == '200':
            self.changeStatus(0, 'signature verified', 'check')
            self.changeStatus(1, 'successfully logged in', 'check')
            jwt = res_data['jwt']
        else:
            self.changeStatus(1, res_data['msg'], 'wrong')


    def changeStatus(self, index, text, icon):
        l = len(text)
        for i in range(25 - l):
            text += ' '
        status = self.statuses[index]
        status[1].setPixmap(qg.QPixmap("img/%s.png" % icon))
        status[2].setText(' ' + text)

    def clearStatuses(self):
        for i in range(len(self.statuses)):
            self.changeStatus(i, '', 'blank')


if __name__ == '__main__':
    app = qw.QApplication(sys.argv)
    gui = QtGui2()

    sys.exit(app.exec_())
