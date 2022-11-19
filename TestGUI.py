from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont
from PyQt5 import uic
from ReceiveSendData import stream_data


class MyGUI(QMainWindow):

    def __init__(self):
        super(MyGUI,self).__init__()
        uic.loadUi("testGUI.ui",self)
        self.show()

        self.push1.clicked.connect(self.startStream)

    def startStream(self):
        self.label_2.setText("Stream Started")
        port = '/dev/cu.usbserial-A6027M9K'
        portname = self.lineEdit.text()
        port = portname
        srate = 10
        stream_name = 'EdgeBCI'
        stream_type = 'fNIRS'
        num_channels = 2
        is_debug = False
        stream_data(port, srate, stream_name, stream_type, num_channels, is_debug)


def main():
    app = QApplication([])
    window = MyGUI()
    app.exec_()

if __name__ == '__main__':
    main()
