from Interface import Ui_Wizualizator_audio
from PySide6.QtWidgets import (QApplication, QMainWindow)
from AppFunction import AppFunctionService
import sys


if __name__ == "__main__":    
    app = QApplication(sys.argv)
    Wizualizator_audio = QMainWindow()
    ui = Ui_Wizualizator_audio()
    ui.setupUi(Wizualizator_audio)
    appService = AppFunctionService(ui)
    ui.openFileBTN.clicked.connect(appService.readFile)
    Wizualizator_audio.show()
    sys.exit(app.exec())