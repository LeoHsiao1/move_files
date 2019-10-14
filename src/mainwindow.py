import os
import re
import shutil
import sys
import traceback
from fnmatch import fnmatch

from PyQt5 import uic
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import (QApplication, QDesktopWidget, QFileDialog,
                             QMainWindow, QMessageBox)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("mainwindow.ui", self)
        self.center()

    def logger(self, string, end='\n'):  # 定义接收log信号的槽函数
        """ 接收log信号的槽函数，用于记录日志 """
        self.log_view.moveCursor(QTextCursor.End)
        self.log_view.insertPlainText(str(string) + end)

    def center(self):
        """ 使窗口显示在屏幕中心 """
        center = QDesktopWidget().availableGeometry().center()  # 获取屏幕的中心点
        geometry = self.geometry()
        geometry.moveCenter(center)
        self.setGeometry(geometry)

    def choose_src_dir_slot(self):
        _dir = QFileDialog.getExistingDirectory(w, "选择目录", ".")
        self.src_dir.setText(_dir)

    def choose_dst_dir_slot(self):
        _dir = QFileDialog.getExistingDirectory(w, "选择目录", ".")
        self.dst_dir.setText(_dir)

    def start(self):
        """ 按下开始按钮则触发该函数，开始移动或拷贝文件。 """
        try:
            # 暂存变量，防止在运行过程中被用户修改，也避免重复获取的耗时
            operation_name = self.comboBox.currentText()
            src_dir = self.src_dir.text()
            dst_dir = self.dst_dir.text()
            file_pattern = self.file_pattern.text()

            # 启用进度条
            self.logger("【开始】")
            self.progressBar.setEnabled(True)
            self.progressBar.setValue(0)

            # 判断是移动还是拷贝
            if operation_name == "移动":
                __transfer_files = shutil.move
            elif operation_name == "拷贝":
                __transfer_files = shutil.copy

            # 检查输入的目录是否有效
            if not os.path.isdir(src_dir):
                raise ValueError('输入的目录不存在：{}'.format(src_dir))
            if not os.path.isdir(dst_dir):
                raise ValueError('输入的目录不存在：{}'.format(dst_dir))

            # 定义match()函数，用于判断文件名是否匹配
            if self.regular_match_flag.isChecked():
                try:
                    pattern = re.compile(file_pattern)
                except re.error as e:
                    raise ValueError("文件名不是有效的正则表达式：{}".format(e))

                def match(name, pattern):
                    return re.search(pattern, name)  # 采用正则匹配
            else:
                match = fnmatch  # 采用通配符匹配

            # 更新进度
            self.logger("准备{}...".format(operation_name))
            self.logger("寻找名字匹配的所有文件...")
            self.progressBar.setValue(5)

            # 查找名字匹配的所有文件
            src_files = []
            for basepath, dirnames, filenames in os.walk(src_dir, onerror=self.logger):
                for filename in filenames:
                    if match(filename, file_pattern):
                        src_files.append(os.path.join(basepath, filename))
            length = len(src_files)

            # 更新进度
            self.logger("名字匹配的文件一共有{}个".format(length))
            self.progressBar.setValue(10)

            # 进行移动或拷贝
            for i, path in enumerate(src_files):
                __transfer_files(path, dst_dir)

                self.logger("已处理：{}".format(path))
                self.progressBar.setValue(10 + 90 * ((i+1) / length))   # 更新进度

            # 使进度条失效
            self.progressBar.setValue(100)
            self.progressBar.setEnabled(False)
            self.logger("【结束】\n\n")
            QMessageBox.information(self, "提示", "成功完成！")

        except Exception as e:
            # self.logger(traceback.format_exc())
            self.logger("错误：" + str(e))
            QMessageBox.critical(self, "错误", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
