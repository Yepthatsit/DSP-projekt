import sounddevice as sd
from PyQt6.QtWidgets import QFileDialog
import audioread
import pyqtgraph as pg
from PySide6.QtCore import Qt,Signal
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
        self.Anim1Thread = threading.Thread(target=self.animateAndPlayAudio, daemon=True)
        self.Anim1Thread.start()
        self.audioQueue = queue.Queue()
        self.line1 = self.ui.line1
        self.signals = self.ui.signals
    
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
                    self.channels = audio_file.channels
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
        while True:
            while not self.stopAudioThreadEvent.is_set():
                try:
                    data = self.audioQueue.get(timeout=0.1)  # wait max 100ms
                    self.stream.write(data)
                except:
                    continue  # no data available yet
            time.sleep(0.01)  # avoid busy waiting
    def animateAndPlayAudio(self):
        #https://stackoverflow.com/questions/64307813/pyqtgraph-stops-updating-and-freezes-when-grapahing-live-sensor-data
        #if not self.audio_data.any():
        #    return 
        skipData = 10
        capacity = self.frameSize * self.numFramesPlottedInPlot1
        display_len = capacity // skipData
        while True:
            start = time.time()
            if not self.StartEvent.is_set():
                self.StartEvent.wait()
            while self.stopAudioThreadEvent.is_set():
                time.sleep(0.01)
            if self.current_frame == 0:
                #self.audioQueue.put_nowait(chunk_data)
                self.current_frame += self.frameSize*self.numFramesPlottedInPlot1
                self.y = list(self.audio_data[:self.numFramesPlottedInPlot1*self.frameSize:skipData])
                self.x = list(self.time_axis[:self.numFramesPlottedInPlot1*self.frameSize:skipData])
                self.current_frame = self.numFramesPlottedInPlot1*self.frameSize
            rawChunk = self.audio_data[self.current_frame:self.current_frame + self.frameSize]
            newTimeChunk = self.time_axis[self.current_frame:self.current_frame + self.frameSize:skipData]
            newChunk = rawChunk[::skipData]
            try:
                self.audioQueue.put_nowait(rawChunk)  # send new audio chunk to the queue
            except:
                pass
            self.x.extend(newTimeChunk)
            self.y.extend(newChunk)
            self.x = self.x[-display_len:]
            self.y = self.y[-display_len:]
            self.ui.signals.UpdateGraphSignal.emit(self.x, self.y)  # emit signal to update the graph
           #line set data maight have to be done in the main thread
            #self.line1.setData(self.x, self.y)
            #self.UpdateGraphSignal.emit()
            self.current_frame += self.frameSize
            if self.current_frame + self.frameSize >=len(self.audio_data) or self.CancelEvent.is_set():
                self.StartEvent.clear()
                self.CancelEvent.clear()
                #self.CancelButtonClicked()
            while time.time() - start < self.frameSize / self.SampleRate - 10/self.SampleRate:  
                time.sleep(0.001)  # wait until the next frame is ready or cancelled
        
        
    def PauseButtonClicked(self):
        if not self.stopAudioThreadEvent.is_set():
            self.stopAudioThreadEvent.set()
            print("Playback paused.")
            fade = np.zeros(256, dtype='int16')
            try:
                self.audioQueue.put_nowait(fade)  # send a fade-out signal
            except:
                pass
            #self.stream.stop()
            self.ui.PRBTN.setText("Odtwarzaj")
        else:
            self.stopAudioThreadEvent.clear()
            #self.stream.start()
            fade = np.zeros(256, dtype='int16')
            try:
                self.audioQueue.put_nowait(fade)  # send a fade-in signal
            except:
                pass
            self.ui.PRBTN.setText("Pauza")
            print("Playback resumed.")
            
    def visualizeAndPlayAudio(self):
        if not self.SelectedFilePath:
            print("No file selected. Please select a file first.")
            return
        if not self.audio_data.any():
            print("No audio data loaded. Please load a file first.")
            return
        self.stopAudioThreadEvent.clear()
        self.CancelEvent.clear()
        self.ui.PRBTN.setText("Pauza")
        #self.x = self.y = []
        self.line1.clear()
        self.ui.plotWidget.setYRange(min(self.audio_data), max(self.audio_data), padding=0)
        self.ui.plotWidget.setLabel('left', 'Amplitude')
        self.ui.plotWidget.setLabel('bottom', 'Time (s)')
        self.ui.plotWidget.setTitle('Audio waveform')
        #self.ui.plotWidget.showGrid(x=True, y=True)
        self.ui.plotWidget.setMouseEnabled(x=False, y=False)
        self.current_frame = 0
        self.stream = sd.OutputStream(samplerate=self.SampleRate,channels=1, dtype='int16')
        self.stream.start()
        self.StartEvent.set()
        self.ui.StartBTN.setEnabled(False)
        #self.ui.StartBTN.setDown(True)
        self.ui.openFileBTN.setEnabled(False)
        self.ui.CancelBTN.setEnabled(True)
        self.ui.PRBTN.setEnabled(True)
        
    def CancelButtonClicked(self):
        self.CancelEvent.set()
        self.StartEvent.clear()
        self.stopAudioThreadEvent.clear()
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
        self.ui.StartBTN.setEnabled(True)
        self.ui.openFileBTN.setEnabled(True)
        self.ui.CancelBTN.setEnabled(False)
        self.ui.CancelBTN.setDown(False)
        self.ui.PRBTN.setEnabled(False)
        self.ui.PRBTN.setText("Pauza")
        print("Playback cancelled.")