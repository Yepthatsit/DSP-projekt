from PyQt6.QtWidgets import QFileDialog
from PySide6.QtCore import Qt,Signal
from scipy.fft import fft,fftfreq
from scipy.signal import iirfilter,sosfilt,tf2sos
from Interface import Ui_Wizualizator_audio
import sounddevice as sd
import pyqtgraph as pg
import numpy as np
import audioread
import numba
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
        self.numFramesPlottedInPlot1 = 100
        self.stream = None
        self.stopAudioThreadEvent = threading.Event()
        self.CancelEvent = threading.Event()
        self.StartEvent = threading.Event()
        self.LevelsEavent = threading.Event()
        self.current_frame = 0
        self.audioThread = threading.Thread(target=self.playAudioChunk,daemon=True)
        self.audioThread.start()
        self.Anim1Thread = threading.Thread(target=self.animateAndPlayAudio, daemon=True)
        self.Anim1Thread.start()
        self.Anim2Thread = threading.Thread(target=self.CalculateLevelsThread ,daemon=True)
        self.Anim2Thread.start()
        self.audioQueue = queue.Queue()
        self.line1 = self.ui.line1
        self.signals = self.ui.signals
        self.bands = [
                        (11.1, 12.5, 14.0),
                        (14.3, 16.0, 18.0),
                        (17.8, 20.0, 22.4),
                        (22.3, 25.0, 28.1),
                        (28.1, 31.5, 35.4),
                        (35.6, 40.0, 44.9),
                        (44.5, 50.0, 56.1),
                        (56.1, 63.0, 70.7),
                        (71.3, 80.0, 89.8),
                        (89.1, 100.0, 112.2),
                        (111.4, 125.0, 140.3),
                        (142.5, 160.0, 179.6),
                        (178.2, 200.0, 224.5),
                        (222.7, 250.0, 280.6),
                        (280.6, 315.0, 353.6),
                        (356.4, 400.0, 449.0),
                        (445.4, 500.0, 561.2),
                        (561.3, 630.0, 707.2),
                        (712.7, 800.0, 898.0),
                        (890.9, 1000.0, 1122.5),
                        (1113.6, 1250.0, 1403.1),
                        (1425.4, 1600.0, 1795.9),
                        (1781.8, 2000.0, 2244.9),
                        (2227.2, 2500.0, 2806.2),
                        (2806.3, 3150.0, 3535.8),
                        (3563.6, 4000.0, 4489.8),
                        (4454.5, 5000.0, 5612.3),
                        (5612.7, 6300.0, 7071.5),
                        (7127.2, 8000.0, 8979.7),
                        (8909.0, 10000.0, 11224.6),
                        (11136.2, 12500.0, 14030.8),
                        (14254.4, 16000.0, 17959.4),
                        (17818.0, 20000.0, 22000.0)
                    ]
        self.levels = []
    
    def AppShutdown(self):
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
        self.audioThread.join(timeout=0)
        self.Anim1Thread.join(timeout=0)
        self.Anim2Thread.join(timeout=0)
    
    def CalculateLevelsThread(self):
        while True:
            if not self.LevelsEavent.is_set():
                self.LevelsEavent.wait()
            #start = time.time()
            
            levels = np.empty(len(self.filters), dtype=np.float64)
            Chunk = self.audio_data[self.current_frame: self.current_frame + self.numFramesPlottedInPlot1*self.frameSize]
            for i, fil in enumerate(self.filters):
                filtered = sosfilt(fil, Chunk)
                levels[i] = 20 * np.log10(np.mean(filtered **2) + 1e-12)
            #print(f"{time.time() - start} {time.time() - start < self.frameSize / self.SampleRate - 50/self.SampleRate}")
            self.signals.UpdateLevels.emit(levels)
            self.LevelsEavent.clear()
                
            
    
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
                self.filters = []
                for band in self.bands:
                    sos = iirfilter(4, [band[0], band[2]], btype='band', ftype='butter',output = 'sos', fs=self.SampleRate)
                    self.filters.append(sos)
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
                self.LevelsEavent.set()
                
                self.y = list(self.audio_data[:self.numFramesPlottedInPlot1*self.frameSize:skipData])
                self.x = list(self.time_axis[:self.numFramesPlottedInPlot1*self.frameSize:skipData])
                #freq, amp = fftfreq(len(self.y), 1/self.SampleRate),fft(self.y)
                while self.LevelsEavent.is_set():
                    time.sleep(0.001)
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
            self.LevelsEavent.set()
            self.ui.signals.UpdateGraphSignal.emit(self.x, self.y)  # emit signal to update the graph
           #line set data maight have to be done in the main thread
            #self.line1.setData(self.x, self.y)
            #self.UpdateGraphSignal.emit()
            self.current_frame += self.frameSize
            if self.current_frame + self.frameSize >=len(self.audio_data) or self.CancelEvent.is_set():
                self.StartEvent.clear()
                self.CancelEvent.clear()
                #self.CancelButtonClicked()
            while time.time() - start < self.frameSize / self.SampleRate - 55/self.SampleRate:  
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
        self.ui.plotWidget_2.setMouseEnabled(x=False, y=False)
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