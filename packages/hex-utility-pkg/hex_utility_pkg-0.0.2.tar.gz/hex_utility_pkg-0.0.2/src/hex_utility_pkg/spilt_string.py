import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui

class SplitStringWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.hello = ["Hallo Welt", "Hei maailma", "Hola Mundo", "Привет мир"]
        self.button = QtWidgets.QPushButton("16进制数转ASCII字符串")
    
        self.SoureHexDataEdit =  QtWidgets.QTextEdit()
        self.StringSpiltEdit = QtWidgets.QTextEdit()
        self.ASCII_String_Edit = QtWidgets.QTextEdit()

        self.SoureHexDataEdit.setPlaceholderText("16进制转字符串,请填入16进制字符串，支持空格，\",\", \"-\"分隔符。")
        self.StringSpiltEdit.setPlaceholderText("分隔后的字符串：")
        self.ASCII_String_Edit.setPlaceholderText("转换后的字符串:")
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.SoureHexDataEdit)
        self.layout.addWidget(self.StringSpiltEdit)
        self.layout.addWidget(self.ASCII_String_Edit)
        self.layout.addWidget(self.button)
        self.button.clicked.connect(self.calculateSumBtnHandle)

  
    @QtCore.Slot()
    def calculateSumBtnHandle(self):
        origin_string =  self.SoureHexDataEdit.toPlainText()
        filter_str = origin_string.replace(',','').replace('-','').replace(' ','')
        spilt_string = [filter_str[i:i+2] for i in range(0,len(filter_str),2)]

        spilt_string_with_seperator = ""
        for s in spilt_string:
            spilt_string_with_seperator += s
            spilt_string_with_seperator += ' '
        self.StringSpiltEdit.setText(spilt_string_with_seperator)
        print(spilt_string)

        ascii_string = ""
        for s in spilt_string:
            ascii_string += chr(int(s,16))
        print(ascii_string)
        self.ASCII_String_Edit.setText(ascii_string)

if __name__ == "__main__":
    print("split_string func is running.!")
    app = QtWidgets.QApplication([])

    widget = SplitStringWidget()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec()) 