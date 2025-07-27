import asyncio
from tkinter import filedialog
import audioread
class AppFunctionService:
    def __init__(self, app):
        self.SelectedFilePath = ""
        self.SampleRate = 0
        self.FileBytes = []
        self.frameSize = 1024
        
    async def readFile(self):
        filepath = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3 *.flac")])
        if filepath:
            self.SelectedFilePath = filepath
            self.FileBytes = []
            self.SampleRate = 0
            
            async with audioread.audio_open(filepath) as audio_file:
                self.SampleRate = audio_file.samplerate
                self.FileBytes = audio_file.read_data()
            
            print(f"File {self.SelectedFilePath} loaded with sample rate {self.SampleRate} Hz.")
        else:
            print("No file selected.")