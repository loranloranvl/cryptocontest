import socket
import json
import logging
import time
import sys
import ecckeygen
import os
import decrypt
from functools import partial
from gmssl import func, sm2
import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg
from PyQt5.QtCore import Qt

def recv_except():
    try:
        return sock.recv(MAX_BYTES)
    except (ConnectionResetError, socket.timeout) as e:
        print('[ERROR]', e)
        return None

MAX_BYTES = 4096
jwt = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImxvcmFuIiwicHVia2V5IjoiYjJiZTNiYjY3YWVmYTZlNmJiMjNmN2FkOGFiMTNiYjI1YjE0ZTg1MjAyYzg4NDk1MTg3ZGUwOTY0OGJjNjUzNzNiNzYzNjczM2NkN2Q1Y2I0NmJhN2JkYWEzZThhZGQxZGU3MmFjZWQyMGZhOTE5NjkxNjQ1MGQ1YTYzODg3NGQifQ.AOZyBVVR1litwPYohBdFxUWHYK_rBPhG2A1UKQ7pCkg"
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(2)
sock.connect(('127.0.0.1', 51742))
gui = None
keys = None
# print(sock.recvfrom(4096))


def layoutCenter(box, *items):
    box.addStretch(1)
    for item in items:
        box.addWidget(item)
    box.addStretch(1)


class QtGui(qw.QWidget):
    def __init__(self):
        super().__init__()

        # status object at the bottom middle part of the window
        self.statuses = []

        # 
        self.req_filename = ''
        self.files = []

        self.initUI()
        self.getFileList()

    def initUI(self):
        lLabel = qw.QLabel("Upload New Files")
        lLabelHbox = qw.QHBoxLayout()
        layoutCenter(lLabelHbox, lLabel)

        myBold = qg.QFont()
        myBold.setBold(True)

        rLabel = qw.QLabel("Available Files")
        rLabelHbox = qw.QHBoxLayout()
        layoutCenter(rLabelHbox, rLabel)

        for label in [lLabel, rLabel]:
            label.setStyleSheet('''
                color: #333;
                font-size: 60px;
                font-family: Maiandra GD;
            ''')
            label.setFont(myBold)

        lSelect = qw.QPushButton("Select New File")
        lSelectHbox = qw.QHBoxLayout()
        layoutCenter(lSelectHbox, lSelect)
        lSelect.setStyleSheet('''
            QPushButton {
                color: #666;
                border: 20px dashed #ddd;
                padding: 50px 42px;
                font-size: 50px;
                font-family: Maiandra GD;
                margin-bottom: 15px;
            }
            QPushButton:hover {
                color: #333;
                border-color: #ccc;
            }
        ''')
        lSelect.clicked.connect(self.handleSelect)

        self.lFile = qw.QLabel("")
        self.lFile.setStyleSheet('''
            QLabel {
                font-family: Maiandra GD;
            }
        ''')
        lFileHbox = qw.QHBoxLayout()
        layoutCenter(lFileHbox, self.lFile)
        self.lFile.setStyleSheet('''
            color: #333;
            font-size: 30px;
            font-family: Maiandra GD;
        ''')

        for i in range(5):
            icon = qw.QLabel()
            icon.setPixmap(qg.QPixmap("img/blank.png"))
            rfile = qw.QPushButton('foobarbaz')
            rfile.setCursor(qg.QCursor(Qt.PointingHandCursor))
            hbox = qw.QHBoxLayout()
            layoutCenter(hbox, rfile, icon)
            rfile.setStyleSheet('''
                QPushButton {
                    color: #666;
                    font-size: 40px;
                    margin-bottom: -2px;
                    background-color: white;
                    border: none;
                    font-family: Maiandra GD;
                }
                QPushButton:hover {
                    color: #444;
                }
            ''')
            self.files.append((hbox, rfile, icon))

        lBtn = qw.QPushButton("Upload File")
        lBtnHbox = qw.QHBoxLayout()
        layoutCenter(lBtnHbox, lBtn)
        lBtn.clicked.connect(self.handleUpload)

        rBtn = qw.QPushButton("Request File")
        rBtn.clicked.connect(self.handleRequest)
        rBtnHbox = qw.QHBoxLayout()
        layoutCenter(rBtnHbox, rBtn)

        for btn in [lBtn, rBtn]:
            btn.setStyleSheet('''
                QPushButton {
                    border: none;
                    padding: 12px 18px;
                    font-family: Maiandra GD;
                    font-size: 35px;
                    color: white;
                    background-color: #33adff;
                }
                QPushButton:hover {
                    background-color: #1aa3ff;
                }
            ''')

        for btn in [lSelect, lBtn, rBtn]:
            btn.setCursor(qg.QCursor(Qt.PointingHandCursor))

        lVbox = qw.QVBoxLayout()
        lVbox.addLayout(lLabelHbox)
        lVbox.addStretch(1)
        lVbox.addLayout(lSelectHbox)
        lVbox.addLayout(lFileHbox)
        lVbox.addStretch(1)
        lVbox.addLayout(lBtnHbox)
        lVbox.addStretch(1)

        rVbox = qw.QVBoxLayout()
        rVbox.addLayout(rLabelHbox)
        rVbox.addStretch(1)
        for file in self.files:
            rVbox.addLayout(file[0])
        rVbox.addStretch(1)
        rVbox.addLayout(rBtnHbox)
        rVbox.addStretch(1)

        mSeperator = qw.QPushButton('')
        mSeperator.setStyleSheet('''
            width: 0;
            height: 500px;
            border-left: 2px solid #f3f3f3;
            border-right: 2px solid #f3f3f3;
            border-top: none;
            border-bottom: none;
        ''')
        mVbox = qw.QVBoxLayout()
        layoutCenter(mVbox, mSeperator)

        hhbox = qw.QHBoxLayout()
        hhbox.addLayout(lVbox)
        hhbox.addLayout(mVbox)
        hhbox.addLayout(rVbox)

        for i in range(2):
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

        self.clearStatuses()

        vbox = qw.QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hhbox, 18)
        for status in self.statuses:
            vbox.addLayout(status[0])
        vbox.addStretch(1)

        self.setLayout(vbox)

        width = 1200
        height = width / 1.618
        self.setGeometry(300, 90, width, height)
        self.setWindowTitle('D3CRYPT')
        self.setWindowIcon(qg.QIcon('img/bitbug.ico'))
        self.setStyleSheet("background-color: white;")

        qtRectangle = self.frameGeometry()
        centerPoint = qw.QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self.show()

    def changeStatus(self, index, text, icon):
        l = len(text)
        left = True
        for i in range(26 - l):
            if left:
                text = ' ' + text
            else:
                text += ' '
            left = not left
        status = self.statuses[index]
        status[1].setPixmap(qg.QPixmap("img/%s.png" % icon))
        status[2].setText(text)

    def clearStatuses(self):
        self.changeStatus(0, 'server currently connected', 'link')
        self.changeStatus(1, '', 'blank')

    def handleSelect(self):
        # gray box click handler
        self.clearStatuses()
        fname = qw.QFileDialog.getOpenFileName(self, 'Open file', '.')
        if fname[0]:
            self.selectedFile = fname[0]
            self.lFile.setText(fname[0].split('/')[-1])

    def handleRfileSelect(self, index, filename):
        # rfile click handler - display green check icon
        self.clearStatuses()
        self.req_filename = filename
        for file in self.files:
            file[1].setStyleSheet('''
                QPushButton {
                    color: #333;
                    font-size: 40px;
                    margin-bottom: -2px;
                    background-color: white;
                    border: none;
                    font-family: Maiandra GD;
                }
            ''')
            file[2].setPixmap(qg.QPixmap('img/blank.png'))
        self.files[index][1].setStyleSheet('''
            QPushButton {
                color: #666;
                font-size: 40px;
                margin-bottom: -2px;
                background-color: white;
                border: none;
                font-family: Maiandra GD;
            }
            QPushButton:hover {
                color: #444;
            }
        ''')
        self.files[index][2].setPixmap(qg.QPixmap('img/select.png'))

    def handleUpload(self):
        self.clearStatuses()
        try:
            with open(self.selectedFile, 'rb') as f:
                file_length = len(f.read())
        except AttributeError:
            self.changeStatus(1, 'select your file first', 'wrong')
            return
        req_data = json.dumps({
            'jwt': jwt,
            'mode': 'UP',
            'length': file_length,
            'name': self.selectedFile.split('/')[-1]
        })

        self.changeStatus(1, 'uploading selected file', 'loader')
        sock.send(req_data.encode('ascii'))
        res = recv_except()
        if res == None:
            return
        res_data = json.loads(res.decode('ascii'))
        if res_data['status'] == '201':
            sent_len = 0
            with open(self.selectedFile, 'rb') as f:
                while sent_len < file_length:
                    sock.send(f.read(MAX_BYTES))
                    sent_len += MAX_BYTES
        else:
            self.changeStatus(1, res_data['msg'], 'wrong')
            return

        res = recv_except()
        if res == None:
            return
        res_data = json.loads(res.decode('ascii'))
        if res_data['status'] == '200':
            self.changeStatus(1, 'file successfully uploaded', 'check')
            self.getFileList()

    def getFileList(self):
        self.clearStatuses()
        self.changeStatus(1, 'fetching file list', 'loader')
        for rfile in self.files:
            rfile[1].setText('')
            rfile[2].setPixmap(qg.QPixmap("img/blank.png"))
        req_data = json.dumps({
            'mode': 'FILELIST',
            'jwt': jwt    
        })
        sock.send(req_data.encode('ascii'))
        res = None
        try:
            res = sock.recv(MAX_BYTES).decode('ascii')
        except (ConnectionResetError, socket.timeout) as e:
            print('[ERROR]:', e)
            self.clearStatuses()
            self.changeStatus(0, 'server timeout', 'wrong')
            return
        res_data = json.loads(res)
        if res_data['status'] == '200':
            self.changeStatus(1, 'file list updated', 'check')

            for i, v in enumerate(res_data['names']):
                self.files[i][1].setText(v)
                self.files[i][1].clicked.connect(partial(self.handleRfileSelect, i, v))

    def handleRequest(self):
        # request file click handler
        self.clearStatuses()
        if self.req_filename == '':
            self.changeStatus(1, 'choose a file to view', 'wrong')
            return
        req_data = json.dumps({
            'mode': 'DOWN',
            'jwt': jwt,
            'name': self.req_filename
        })
        sock.send(req_data.encode('ascii'))

        self.changeStatus(1, 'sending download request', 'loader')
        res = None
        try:
            res = sock.recv(MAX_BYTES).decode('ascii')
        except socket.timeout:
            self.changeStatus(1, 'request timeout', 'wrong')
            return
        res_data = json.loads(res)

        if res_data['status'] == '200':
            self.changeStatus(1, 'downloading the file', 'loader')
            dec_key = res_data['enc_pvtkey']
            file_length = int(res_data['length'])
            file_data = b''
            while len(file_data) < file_length:
                file_data += sock.recv(MAX_BYTES)

        res = recv_except()
        if res == None:
            return
        res_data = json.loads(res.decode('ascii'))

        if res_data['status'] == '200':
            self.changeStatus(1, 'download completed', 'check')
            info_raw = {
                'id': keys['username'].ljust(6, ' '),
                'private key': keys['pvtkey'],
                'decrypt key': dec_key
            }
            pv = decrypt.decrypt(info_raw, file_data)
            if type(pv) == str:
                self.changeStatus(1, pv, 'wrong')
                return
            req_data = json.dumps({
                'mode': 'CHAIN',
                'jwt': jwt,
                'name': self.req_filename,
                'pv': pv
            })
            sock.send(req_data.encode('ascii'))
            res = recv_except()


class QtGui2(qw.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.connected = False
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
                    font-family: Maiandra GD;
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
        self.clearStatuses()

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
        self.setWindowIcon(qg.QIcon('img/bitbug.ico'))
        self.setStyleSheet("background-color: white;")

        # center align
        qtRectangle = self.frameGeometry()
        centerPoint = qw.QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self.show()
        self.testLink()

    def testLink(self):
        self.clearStatuses()
        req_data = json.dumps({
            'mode': 'TEST'
        })
        sock.send(req_data.encode('ascii'))

        req_data = None
        try:
            req_data = sock.recv(MAX_BYTES)
        except (ConnectionResetError, socket.timeout) as e:
            print('[ERROR]:', e)
            self.changeStatus(0, 'connection timeout', 'wrong')
            self.connected = False
        else:
            self.connected = True
            self.clearStatuses()

    def changeStatus(self, index, text, icon):
        l = len(text)
        for i in range(25 - l):
            text += ' '
        status = self.statuses[index]
        status[1].setPixmap(qg.QPixmap("img/%s.png" % icon))
        status[2].setText(' ' + text)

    def clearStatuses(self):
        if self.connected:
            self.changeStatus(0, 'client now established', 'link')
        for i in range(1, len(self.statuses)):
            self.changeStatus(i, '', 'blank')


    def handleRegister(self):
        if not self.connected:
            return
        self.clearStatuses()
        username, ok = qw.QInputDialog.getText(self, 'name', 
                   'Enter your name:')
        if not ok:
            return

        keys = ecckeygen.generate()
        self.changeStatus(0, 'sm2 key-pair generated', 'check')

        self.changeStatus(1, 'posting public key', 'loader')
        req_data = json.dumps({
            'mode': 'REGISTER',
            'username': username,
            'pubkey': keys['pubkey']
        })
        sock.send(req_data.encode('ascii'))
        res = recv_except()
        if res == None:
            return
        res_data = json.loads(res.decode('ascii'))
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
        if not self.connected:
            return
        global jwt
        self.clearStatuses()
        username, ok = qw.QInputDialog.getText(self, 'name', 
                   'Enter your name:')
        if not ok:
            return

        global keys
        self.changeStatus(0, 'searching local keys', 'loading')
        # time.sleep(500)
        found = False
        for filename in os.listdir('.'):
            if filename == "%s_keys.json" % username:
                found = True
                with open(filename, 'r') as f:
                    keys = json.loads(f.read())
        if not found:
            self.changeStatus(1, 'keys.json not found', 'question')
            self.changeStatus(2, 'please select it yourself', 'question')
            # time.sleep(500)
            fname = qw.QFileDialog.getOpenFileName(self, 'select keys.json', '.')
            if not fname[0]:
                self.clearStatuses()
                return
            if filename == ("%s_keys.json" % username):
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
        res = recv_except()
        if res == None:
            return
        res_data = json.loads(res.decode('ascii'))
        if res_data['status'] == '200':
            self.changeStatus(0, 'signature verified', 'check')
            self.changeStatus(1, 'successfully logged in', 'check')
            jwt = res_data['jwt']
            self.close()
            gui.show()
        else:
            self.changeStatus(1, res_data['msg'], 'wrong')


if __name__ == '__main__':
    app = qw.QApplication(sys.argv)
    gui_index = QtGui2()
    gui = QtGui()
    gui.close()
    app.exec_()
