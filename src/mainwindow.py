import os
import re
import shutil
import sys
from fnmatch import fnmatch

from PyQt5 import uic
from PyQt5.QtWidgets import (QApplication, QDesktopWidget, QFileDialog,
                             QMainWindow)
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QTextCursor


class EmittingStream(QObject):
    output = pyqtSignal(str)  	# 定义output信号，接收一个str参数

    def write(self, text):
        self.output.emit(str(text))

    def flush(self):
        pass


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("mainwindow.ui", self)
        self.center()

        # 重定向stdout、stderr，让它们触发output信号，并把信号绑定到logger槽函数
        sys.stdout = EmittingStream(output=self.logger)
        # sys.stderr = sys.stdout

    def logger(self, text):  # 定义接收log信号的槽函数
        """ 接收log信号的槽函数，用于记录日志 """
        self.log_view.moveCursor(QTextCursor.End)
        self.log_view.insertPlainText(text)

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
            self.dst_dir.setText(_dir)

    def start(self):
        """ 按下开始按钮则触发该函数，开始移动或拷贝文件。 """
        # 暂存变量，防止在运行过程中被用户修改，也避免重复获取的耗时
        operation_name = self.comboBox.currentText()
        src_dir = self.src_dir.text()
        dst_dir = self.dst_dir.text()
        file_pattern = self.file_pattern.text()

        # 启用进度条
        print("【开始】")
        self.progressBar.setEnabled(True)
        self.progressBar.setValue(0)

        # 定义match()函数，用于判断文件名是否匹配
        if self.regular_match_flag.isChecked():
            try:
                pattern = re.compile(file_pattern)
            except re.error as e:
                raise ValueError("无效的正则表达式：{}".format(e))

            def match(name, pattern):
                return re.search(pattern, name)  # 采用正则匹配
        else:
            match = fnmatch  # 采用通配符匹配

        # 判断是移动还是拷贝
        if operation_name == "移动":
            __transfer_files = shutil.move
        elif operation_name == "拷贝":
            __transfer_files = shutil.copy
        else:
            raise ValueError('选中的动作不是"移动"或"拷贝"。')

        # 更新进度
        print("准备{}...".format(operation_name))
        print("寻找名字匹配的所有文件...", end="")
        self.progressBar.setValue(5)

        # 查找名字匹配的所有文件
        src_files = []
        for basepath, dirnames, filenames in os.walk(src_dir, onerror=print):
            for filename in filenames:
                if match(filename, file_pattern):
                    src_files.append(os.path.join(basepath, filename))
        length = len(src_files)

        # 更新进度
        print("一共有{}个".format(length))
        self.progressBar.setValue(10)

        # 进行移动或拷贝
        for i, path in enumerate(src_files):
            __transfer_files(path, dst_dir)

            print("已处理：{}".format(path))
            self.progressBar.setValue(10 + 90 * ((i+1) / length))   # 更新进度

        # 使进度条失效
        self.progressBar.setValue(100)
        self.progressBar.setEnabled(False)
        print("【结束】")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
