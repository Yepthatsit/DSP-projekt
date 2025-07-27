from Interface import Ui_Wizualizator_audio
from PySide6.QtWidgets import (QApplication, QMainWindow)
from AppFunction import AppFunctionService
import sys


if __name__ == "__main__":
    appService = AppFunctionService()
        
    app = QApplication(sys.argv)
    Wizualizator_audio = QMainWindow()
    ui = Ui_Wizualizator_audio()
    ui.setupUi(Wizualizator_audio)
    ui.openFileBTN.clicked.connect(lambda : appService.readFile(ui))
    Wizualizator_audio.show()
    sys.exit(app.exec())