import numpy as np
import cv2
import pygame 
from threading import Thread
import time
from PIL import Image
import requests
from requests.auth import HTTPDigestAuth
import subprocess

class Audio(object):
    def __init__(self, audioname = 'Bienvenue.mp3', chunk = 1024  ):
        pygame.init()
        pygame.mixer.init()
        self.audioname = audioname
        self.music = pygame.mixer.music
        self.music.set_volume(0.3)
        self.song = self.music.load(audioname)

        self.thread_audio = Thread(target=self.update_audio, args=())
        self.thread_audio.daemon = True
        self.thread_audio.start()
 
    def update_audio(self):
        print("Play sound !")    
     
class Camera(object):
        def __init__(self, src=0 ):
                self.src = src   
                # FPS = 1/X
                # X = desired FPS
                self.FPS = 1/30
                self.FPS_MS = int(self.FPS * 1000)
                self.capture = cv2.VideoCapture(self.src)
                self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 2)
                self.thread_video = Thread(target=self.update_video, args=())
                self.thread_video.daemon = True
                self.thread_video.start()
                self.frame = None

        def update_video(self):
                while True:
                        if self.capture.isOpened():
                                (self.status, self.frame) = self.capture.read()

                        time.sleep(self.FPS)
        def show_frame(self,name='frame'):
                cv2.imshow(name, self.frame)
                cv2.waitKey(self.FPS_MS)

        def round_int(self,x):
            if x == float("inf") or x == float("-inf"):
                return float(0) # or x or return whatever makes sense
            return x

class Temperature(object):
        def __init__(self, IP="http://169.254.61.84:80"):
                self.IP = IP
                self.username = 'admin'
                self.password = 'vision29'
                self.link = "/ISAPI/Thermal/channels/2/thermometry/1/rulesTemperatureInfo?format=json"
                self.range_temp = requests.get(url=self.IP+self.link, auth=HTTPDigestAuth(self.username,self.password )).json()
                self.average = self.range_temp['ThermometryRulesTemperatureInfoList']['ThermometryRulesTemperatureInfo'][0]['averageTemperature']

if __name__ == '__main__': 
    song = 'Bienvenue.mp3'
    threaded_audio = Audio(song) 
    play_audio = True
    list_IP = ["169.254.61.0/24", "169.254.77.0/24"]
    while True :
            try:

                for id_IP in list_IP:
                        proc = subprocess.run(['nmap','-sP',id_IP], stdout=subprocess.PIPE)
                        out_str = str(proc.stdout)
                        print(out_str)
                        if out_str.find('169') > -1:
                                IP = out_str[out_str.find("169"): out_str.find("\\nHost")]
                threaded_temp = Temperature("http://"+IP)
                print("Temperarute now is " +str(threaded_temp.average) + " °C")
                
                threaded_camera = Camera("rtsp://admin:vision29@169.254.61.84/Streaming/channels/201")
                
                play_audio = True
                if (0<threaded_temp.average<100):
                        print("We are now connected !")
                        break
 
            except:
                if play_audio:
                        threaded_audio.music.play(-1,0.0)
                        play_audio = False
                elif play_audio is False and threaded_audio.music.get_busy() is True :
                        play_audio = True

