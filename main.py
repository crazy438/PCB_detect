import sys
from ultralytics import YOLO # YOLO含Pytorch,Pytorch高版本神秘导包顺序bug，要让YOLO在QT前导入
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import  QApplication
from GUI.main_window import Window

if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    w = Window()
    w.show()
    app.exec_()
