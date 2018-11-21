import sys
import time
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
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont, QCursor
from gmssl.sm4 import CryptSM4, SM4_ENCRYPT, SM4_DECRYPT
from gmssl import sm2, sm3, func

def analyze(file_path):
    result = '<%s>\n' % file_path
    if '.enc' not in file_path:
        return result + 'invalid document\nyou should select a .enc file\n'
    with open(file_path, 'rb') as file:
        file_enc = file.read()
        result += 'total {} bytes'.format(len(file_enc)) + '\n'
    data, end_file = func.destructure(file_enc)
    visited = data['flags'][0] >= 8 * 16
    result += 'visited ' + str(visited) + '\n'
    for key in data:
        if key == 'flags':
            continue
        item = data[key]
        if len(item) > 32:
            result += '{} of length {}'.format(key, len(item))
        elif len(item) > 6:
            result += '{} {}... of length {}'.format(key, item[0:6].hex(), len(item))
        else:
            result += key + ' ' + str(int.from_bytes(data[key], 'big'))
        result += '\n'

    result += '\n'
    for i in range(end_file + 32, len(file_enc), 110):
        info = func.parse_info(file_enc[i:i + 78])
        if i == end_file + 32:
            person_str, role_str = 'creator', 'public key'
        else:
            person_str, role_str = 'visitor', 'signature'
        ip_str = '.'.join([str((info['ip_addr'] >> i) % 256) for i in range(0, 32, 8)][::-1])
        time_str = time.asctime(time.localtime(info['time_stamp']))
        result += '{} {} with ip addr {} at {}\n'.format(person_str, info['id'], ip_str, time_str)
        result += '{} beginning with {}\n'.format(role_str, info['signature'][0:16].upper())
    return result

class QtGui(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.structureLabel = QLabel('Enc-File Analyzer')
        self.structureLabel.setStyleSheet('''
            color: #333;
            font-size: 50px;
            font-weight: 700;
            margin-top: 20px;
            font-family: Maiandra GD;
        ''')

        self.fileBtn = QPushButton('Select File', self)
        self.fileBtn.clicked.connect(self.openFile)
        self.fileBtn.setStyleSheet('''
            background-color: #80aaff;
            color: white;
            margin: 15px;
            padding: 10px 24px;
            border: none;
            font-weight: 1000;
            font-size: 35px;
            font-family: Maiandra GD;
        ''')
        self.fileBtn.setCursor(QCursor(Qt.PointingHandCursor))

        self.structureText = QLabel()
        self.structureText.setStyleSheet('''
            width: 400px;
            color: #333;
            font-size: 25px;
            font-weight: 400;
            padding: 10px;
            margin-bottom: 40px;
            outline: none;
            border: 1.5px solid powderblue;
        ''')
        # self.structureText.setReadOnly(True)

        labelHbox = QHBoxLayout()
        labelHbox.addStretch(1)
        labelHbox.addWidget(self.structureLabel)
        labelHbox.addStretch(1)

        btnHbox = QHBoxLayout()
        btnHbox.addStretch(1)
        btnHbox.addWidget(self.fileBtn)
        btnHbox.addStretch(1)

        textHbox = QHBoxLayout()
        textHbox.addStretch(1)
        textHbox.addWidget(self.structureText)
        textHbox.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(labelHbox)
        vbox.addLayout(btnHbox)
        vbox.addLayout(textHbox)
        vbox.addStretch(1)

        self.setLayout(vbox)

        self.setGeometry(300, 20, 1200, 500)
        self.setWindowTitle('D3CRYPT analyzer')
        self.setWindowIcon(QIcon('img/analyze.png'))
        self.setStyleSheet("background-color: white;")

        self.show()

    def showText(self, content):
        self.structureText.setText(content)

    def openFile(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', '/home')
        if fname[0]:
            self.showText(analyze(fname[0]))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = QtGui()

    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        gui.showText(analyze(file_path))
    else:
        gui.showText('')

    sys.exit(app.exec_())
