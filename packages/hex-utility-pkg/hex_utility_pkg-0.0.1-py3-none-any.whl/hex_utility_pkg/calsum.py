import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui


class CalculateSumWidget(QtWidgets.QWidget):
    
    def __init__(self):
        super().__init__()

        self.hello = ["Hallo Welt", "Hei maailma", "Hola Mundo", "Привет мир"]
        self.button = QtWidgets.QPushButton("计算校验和!")
    
        self.SoureHexDataEdit =  QtWidgets.QTextEdit()
        self.SumEdit = QtWidgets.QTextEdit()
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.SoureHexDataEdit)
        self.layout.addWidget(self.SumEdit)
        self.layout.addWidget(self.button)

        self.button.clicked.connect(self.calculateSumBtnHandle)


    @QtCore.Slot()
    def calculateSumBtnHandle(self):
        sum = 0
        str =  self.SoureHexDataEdit.toPlainText()
        filter_str = str.replace(',','').replace('-','').replace(' ','')
        hex_data_array = bytearray.fromhex(filter_str)
        for value in hex_data_array:
            sum += value
        sum &= 0xff
        self.SumEdit.setText(hex(sum))

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = CalculateSumWidget()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())        