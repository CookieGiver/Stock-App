import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow




class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Trader App')
        self.setFixedSize(QSize(600, 500))
        
        button = QPushButton("Press Me")
        button.setCheckable(False)
        button.clicked.connect(self.the_button_was_clicked)
        self.setCentralWidget(button)

    def the_button_was_clicked(self):
        print("Clicked")

app = QApplication(sys.argv)
window = MainWindow()
window.show()
	
if __name__ == '__main__':
   app.exec()