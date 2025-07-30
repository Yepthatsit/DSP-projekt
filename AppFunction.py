import sounddevice as sd
from PyQt6.QtWidgets import QFileDialog
import audioread
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.animation import FuncAnimation
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
        self.fig1 = plt.figure()
        self.ax1 = self.fig1.add_subplot(111)
        self.numFramesPlottedInPlot1 = 100
        self.stream = None
        self.playAudioChunkEvent = threading.Event()
        self.stopAudioThreadEvent = threading.Event()
        self.current_frame = 0
        self.audioThread = threading.Thread(target=self.playAudioChunk,daemon=True)
        self.audioThread.start()
        self.audioQueue = queue.Queue()
    
    def AppShutdown(self):
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
        if hasattr(self, 'fig1') and self.fig1 is not None:
            plt.close(self.fig1)
        self.audioThread.join(timeout=0)
        
    
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
    def animateAndPlayAudio(self, i):
        start_time = time.perf_counter()
        if not self.audio_data.any():
            return self.line1,
        if i == 0:
            global x
            global y
            x = list(self.time_axis[:self.numFramesPlottedInPlot1*self.frameSize:10])
            y = list(self.audio_data[:self.numFramesPlottedInPlot1*self.frameSize:10])
            self.line1.set_data(x, y)
            self.current_frame = self.numFramesPlottedInPlot1 * self.frameSize
            global max_points
            max_points = int(self.numFramesPlottedInPlot1 * self.frameSize / 10)
            return self.line1,
        start = self.current_frame
        end = start + self.frameSize
        if end >= len(self.audio_data):
            self.anim.event_source.stop()
            self.playAudioChunkEvent.clear()  # Clear the event if end of audio data is reached
            self.stream.stop()
            self.stream.close()
            print("End of audio data reached.")
        chunk_data = self.audio_data[start:end]
        chunk_time = self.time_axis[start:end]
        x.extend(list(chunk_time[::10]))
        y.extend(list(chunk_data[::10]))
        x = x[-max_points:]  
        y = y[-max_points:]  
        
        #sd.play(chunk_data[-self.frameSize:], self.SampleRate)
        #self.stream.write(chunk_data[-self.frameSize:])
        try:
            self.audioQueue.put_nowait(chunk_data)
        except:
            pass
        self.line1.set_data(x, y)
        self.ax1.set_xlim(x[0], x[-1])
        self.current_frame += self.frameSize
        end_time = time.perf_counter()
        frame_time_ms = (end_time - start_time) * 1000
        print(f"Frame render time: {frame_time_ms:.2f} ms")
        return self.line1,
            
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
        matplotlib.use("QtAgg")
        matplotlib.rcParams['toolbar'] = 'None'
        
        if not self.SelectedFilePath:
            print("No file selected. Please select a file first.")
            return
        if not self.audio_data.any():
            print("No audio data loaded. Please load a file first.")
            return
        self.paused = False
        self.ui.PRBTN.setText("Pauza")
        if(self.fig1 is not None):
            plt.close(self.fig1)
        self.fig1 = plt.figure()
        self.ax1 = self.fig1.add_subplot(111)
        self.ax1.set_xlabel('Time [s]')
        self.ax1.set_ylabel('Amplitude')
        self.ax1.set_title('Audio Signal Visualization')
        self.ax1.set_xlim(0, len(self.audio_data) / self.SampleRate)
        self.ax1.set_ylim(np.min(self.audio_data), np.max(self.audio_data))
        self.ax1.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
        self.line1, = self.ax1.plot([], [], lw=2)
        self.fig1.tight_layout()
        self.current_frame = 0
        self.stream = sd.OutputStream(samplerate=self.SampleRate,blocksize=self.frameSize, channels=1, dtype='int16')
        self.stream.start()
        self.anim = FuncAnimation(self.fig1, self.animateAndPlayAudio, interval=self.frameSize*1000/ self.SampleRate, blit=True)#w ms
        self.fig1.show()