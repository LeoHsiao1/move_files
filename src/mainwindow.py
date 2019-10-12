# from PyQt5.QtCore import Qt, QTimer, QDate, QDateTime, QTime
# from PyQt5.QtGui import QIcon, QColor, QFont, QPixmap
import os
import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget, QFileDialog

# os.chdir("src/")

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("mainwindow.ui", self)
        self.center()

    def center(self):
        """ 使窗口显示在屏幕中心 """
        center = QDesktopWidget().availableGeometry().center()  # 获取屏幕的中心点
        geometry = self.geometry()
        geometry.moveCenter(center)
        self.setGeometry(geometry)

    def choose_dir(self):
        _dir = QFileDialog.getExistingDirectory(w, "选择目录", ".")
        if self.sender() == self.choose_src_dir:
            self.src_dir.setText(_dir)
        elif self.sender() == self.choose_dst_dir:
            self.dst_dit.setText(_dir)


app = QApplication(sys.argv)
w = MyWindow()
w.show()
sys.exit(app.exec())
