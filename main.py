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
    app.aboutToQuit.connect(appService.AppShutdown)
    ui.openFileBTN.clicked.connect(appService.readFile)
    ui.StartBTN.clicked.connect(appService.visualizeAndPlayAudio)
    ui.PRBTN.clicked.connect(appService.PauseButtonClicked)
    Wizualizator_audio.show()
    sys.exit(app.exec())