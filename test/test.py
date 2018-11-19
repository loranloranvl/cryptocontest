from PyQt5.QtWidgets import QApplication, QMainWindow

class window(QMainWindow):
    def __init__(self, parent=None):
        super(window, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.Open.clicked.connect(self.openwindow)
        self.openedwin = []

    def openwindow(self):
        windownum = self.ui.windownum.value()
        if windownum != 0:
            if self.openedwin != []:
                for window in self.openedwin:
                    window.close()
            for repeat in range(windownum):
                opennewwindow = newwindow(self)
                # print("opennewwindow:", opennewwindow)
                self.openedwin.append(opennewwindow)
                opennewwindow.show()
        # print("self.openedwin:", self.openedwin)


class newwindow(QMainWindow):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")

if __name__ == "__main__":
    app = QApplication([])
    gui = window()
    gui.show()
    app.exec_()