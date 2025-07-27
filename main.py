from Interface import Ui_Wizualizator_audio
from PySide6.QtWidgets import (QApplication, QMainWindow)
import sys
import AppFunction




if __name__ == "__main__":    
    app = QApplication(sys.argv)
    Wizualizator_audio = QMainWindow()
    ui = Ui_Wizualizator_audio()
    ui.setupUi(Wizualizator_audio)
    ui.pushButton.clicked.connect(lambda: print("Button clicked!"))
    Wizualizator_audio.show()
    sys.exit(app.exec())