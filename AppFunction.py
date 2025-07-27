import asyncio
from PyQt6.QtWidgets import QFileDialog
import audioread
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from Interface import Ui_Wizualizator_audio
import numpy as np
class AppFunctionService:
    def __init__(self,ui:Ui_Wizualizator_audio = None):
        self.SelectedFilePath = ""
        self.SampleRate = 0
        self.FileBytes = []
        self.frameSize = 1024
        self.ui = ui
        self.paused = False
        self.fig1 = plt.figure()
        self.ax1 = self.fig1.add_subplot(111)
        
    def readFile(self):
        print("Reading file...")
        filepath, _ = QFileDialog.getOpenFileName(
            None,
            "Wybierz plik audio",
            "",
            "Pliki audio (*.wav *.mp3)"
        )
        if filepath:
            self.SelectedFilePath = filepath
            self.FileBytes = []
            self.SampleRate = 0
            if(filepath.endswith('.wav')):
                with audioread.audio_open(filepath) as audio_file:
                    self.SampleRate = audio_file.samplerate
                    self.FileBytes = b''.join(audio_file.read_data(-1))
            elif(filepath.endswith('.mp3')):
                print("MP3 files are not supported yet.")
            if(self.ui):
                self.ui.textBrowser.setText(f"Plik: {self.SelectedFilePath.split('/')[-1]}\n")
            print(f"File {self.SelectedFilePath} loaded with sample rate {self.SampleRate} Hz.")
        else:
            print("No file selected.")
    def animateAndPlayAudio(self, i):
        if not self.FileBytes or self.paused:
            return
    
        # Convert bytes to numpy array once
        if not hasattr(self, 'audio_data'):
            self.audio_data = np.frombuffer(self.FileBytes, dtype=np.int16)
            self.time_axis = np.linspace(0, len(self.audio_data) / self.SampleRate, num=len(self.audio_data))
            self.current_frame = 0

        start = self.current_frame
        end = start + self.frameSize

        if start >= len(self.audio_data):
            return  # stop condition

        chunk_data = self.audio_data[start:end]
        chunk_time = self.time_axis[start:end]

        self.ax1.clear()
        self.ax1.plot(chunk_time, chunk_data)
        self.ax1.set_xlabel('Time [s]')
        self.ax1.set_ylabel('Amplitude')
        self.ax1.set_title('Audio Signal Visualization')

        self.current_frame += self.frameSize
            
    def PauseButtonClicked(self):
        self.paused = not self.paused
        if self.paused:
            print("Playback paused.")
        else:
            print("Playback resumed.")
    def visualizeAndPlayAudio(self):
        self.anim = FuncAnimation(self.fig1, self.animateAndPlayAudio, interval=1000)
        plt.show()