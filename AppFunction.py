import sounddevice as sd
from PyQt6.QtWidgets import QFileDialog
import audioread
import pyqtgraph as pg
from PySide6.QtCore import Qt
from Interface import Ui_Wizualizator_audio
import numpy as np
import threading
import queue
import time

class AppFunctionService:
    def __init__(self,ui:Ui_Wizualizator_audio = None):
        self.SelectedFilePath = ""
        self.SampleRate = 0
        self.audio_data = np.array([])
        self.frameSize = 1024 
        self.ui = ui
        self.paused = False
        #self.fig1 = plt.figure()
        #self.ax1 = self.fig1.add_subplot(111)
        self.numFramesPlottedInPlot1 = 100
        self.stream = None
        self.stopAudioThreadEvent = threading.Event()
        self.CancelEvent = threading.Event()
        self.StartEvent = threading.Event()
        self.current_frame = 0
        self.audioThread = threading.Thread(target=self.playAudioChunk,daemon=True)
        self.audioThread.start()
        self.Anim1Thread = threading.Thread(target=self.animateAndPlayAudio, args=(0,), daemon=True)
        self.audioQueue = queue.Queue()
    
    def AppShutdown(self):
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
        self.audioThread.join(timeout=0)
        self.Anim1Thread.join(timeout=0)
        
    
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
            self.audio_data = []
            self.SampleRate = 0
            if(filepath.endswith('.wav')):
                with audioread.audio_open(filepath) as audio_file:
                    self.SampleRate = audio_file.samplerate
                    FileBytes = bytes(int(2.5*self.numFramesPlottedInPlot1*self.frameSize)) + b''.join(audio_file.read_data(-1))
                    self.audio_data = np.frombuffer(FileBytes, dtype=np.int16)
                    self.time_axis = np.linspace(0, len(self.audio_data) / self.SampleRate, num=len(self.audio_data))
            elif(filepath.endswith('.mp3')):
                print("MP3 files are not supported yet.")
            if(self.ui):
                self.ui.textBrowser.setText(f"Plik: {self.SelectedFilePath.split('/')[-1]}\n")
            print(f"File {self.SelectedFilePath} loaded with sample rate {self.SampleRate} Hz.")
        else:
            print("No file selected.")
    def playAudioChunk(self):
         while not self.stopAudioThreadEvent.is_set():
            try:
                data = self.audioQueue.get(timeout=0.1)  # wait max 100ms
                self.stream.write(data)
            except:
                continue  # no data available yet
    def animateAndPlayAudio(self):
        #if not self.audio_data.any():
        #    return 
        chunk_data = self.audio_data[self.current_frame:self.current_frame + self.numFramesPlottedInPlot1*self.frameSize]
        try:
            if self.current_frame == 0:
                self.audioQueue.put_nowait(chunk_data)
            else:
                self.audioQueue.put_nowait(chunk_data[-self.frameSize:])  # only send the last frame size chunk
        except:
            pass
        self.current_frame += self.frameSize
        
        
    def PauseButtonClicked(self):
        self.paused = not self.paused
        if not hasattr(self, 'anim'):
            print("Animation not started yet.")
            return
        if self.paused:
            print("Playback paused.")
            fade = np.zeros(256, dtype='int16')
            self.stream.write(fade)
            #self.stream.stop()
            self.anim.event_source.stop()
            self.ui.PRBTN.setText("Odtwarzaj")
        else:
            #self.stream.start()
            fade = np.zeros(256, dtype='int16')
            self.stream.write(fade)
            self.anim.event_source.start()
            self.ui.PRBTN.setText("Pauza")
            print("Playback resumed.")
            
    def visualizeAndPlayAudio(self):
        if not self.SelectedFilePath:
            print("No file selected. Please select a file first.")
            return
        if not self.audio_data.any():
            print("No audio data loaded. Please load a file first.")
            return
        self.paused = False
        self.ui.PRBTN.setText("Pauza")
        self.ui.plotWidget.clear()
        self.line1 = self.ui.plotWidget.plot(pen='r')
        self.ui.plotWidget.setLabel('left', 'Amplitude')
        self.ui.plotWidget.setLabel('bottom', 'Time (s)')
        self.ui.plotWidget.setTitle('Audio waveform')
        self.ui.plotWidget.showGrid(x=True, y=True)
        self.ui.plotWidget.setMouseEnabled(x=False, y=False)
        self.stream = sd.OutputStream(samplerate=self.SampleRate, blocksize=self.frameSize, channels=1, dtype='int16')
        self.stream.start()
        self.animateAndPlayAudio(0)
        self.ui.StartBTN.setEnabled(False)
        #self.ui.StartBTN.setDown(True)
        self.ui.openFileBTN.setEnabled(False)
        self.ui.CancelBTN.setEnabled(True)
        self.ui.PRBTN.setEnabled(True)
        
    def CancelButtonClicked(self):
        self.stopAudioThreadEvent.set()
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
        self.ui.StartBTN.setEnabled(True)
        self.ui.openFileBTN.setEnabled(True)
        self.ui.CancelBTN.setEnabled(False)
        self.ui.CancelBTN.setDown(False)
        self.ui.plotWidget.clear()
        self.ui.PRBTN.setEnabled(False)
        self.ui.PRBTN.setText("Pauza")
        print("Playback cancelled.")