import asyncio
from PyQt6.QtWidgets import QFileDialog
import audioread
import matplotlib.pyplot as plt
from Interface import Ui_Wizualizator_audio
class AppFunctionService:
    def __init__(self):
        self.SelectedFilePath = ""
        self.SampleRate = 0
        self.FileBytes = []
        self.frameSize = 1024
        
    def readFile(self,ui:Ui_Wizualizator_audio = None):
        print("Reading file...")
        filepath, _ = QFileDialog.getOpenFileName(
            None,
            "Wybierz plik audio",
            "",
            "Pliki audio (*.wav *.mp3 *.flac)"
        )
        if filepath:
            self.SelectedFilePath = filepath
            self.FileBytes = []
            self.SampleRate = 0
            
            with audioread.audio_open(filepath) as audio_file:
                self.SampleRate = audio_file.samplerate
                self.FileBytes = audio_file.read_data()
            if(ui):
                ui.textBrowser.setText(f"Plik: {self.SelectedFilePath.split('/')[-1]}\n")
            print(f"File {self.SelectedFilePath} loaded with sample rate {self.SampleRate} Hz.")
        else:
            print("No file selected.")