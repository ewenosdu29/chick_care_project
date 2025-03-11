import numpy as np
import cv2
import matplotlib.pyplot as plt
import pygame 
from threading import Thread
import time
from PIL import Image
from utils.anchor_generator import generate_anchors
from utils.anchor_decode import decode_bbox
from utils.nms import single_class_non_max_suppression
from load_model.pytorch_loader import load_pytorch_model, pytorch_inference
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable
import requests
from requests.auth import HTTPDigestAuth

################################################
## Methode simple pour calibrer deux cameras:
##    ROI_camera = ((105,975), (330,1510))      # Original: 1920*1080
##    ROI_thermal = ((0,-1), (0,-1))            # Original: 1280*720
##      Min valeur = [-140:-100,-230:-130,0]            # 0:25, 25:50 , 75:100
##      Max valeur = [100:140,-230:-130,0]
################################################

class show_info(object):
        def __init__(self, window = 'Text'):
                self.window = window
                self.thread_show = Thread(target=self.query, args=())
                self.thread_show.daemon = True
                self.thread_show.start()
                
        def query(self):
                image = cv2.imread("./icon/thinking2.png")
                constant=cv2.copyMakeBorder(image,330,10,50,50, cv2.BORDER_CONSTANT,value=[0,0,0] )       
                cv2.namedWindow(self.window, cv2.WND_PROP_FULLSCREEN)
                cv2.setWindowProperty(self.window, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                cv2.imshow(self.window, constant)

        def detect(self, temperature = 37.1, detect= True, mask = False): 
                if mask is True:
                        text_out = ' !!! Merci !!!'
                        color_mask = (0,255,0)
                        img_out = "./icon/thumb2.png"
                else :
                        text_out = 'OBLIGATOIRE!'
                        color_mask = (0,0,255)
                        img_out = "./icon/mask2.png"
	            
                if temperature > 38:
                        color_temp = (0,0,255)
                elif temperature < 34:
                        color_temp = (0,0,0)
                else:
                        color_temp = (0,255,0)
                image = cv2.imread(img_out)
                constant=cv2.copyMakeBorder(image,330,10,50,50,cv2.BORDER_CONSTANT,value=[0,0,0] )
                cv2.putText(constant, text_out,(0,70), cv2.FONT_HERSHEY_SIMPLEX, 3,color_mask, 3, 0)
                cv2.putText(constant,"Votre temperature:" ,(5,180), cv2.FONT_HERSHEY_SIMPLEX, 2, color_temp, 10, 3)
                cv2.putText(constant," "+str(temperature)+" C" ,(30,300), cv2.FONT_HERSHEY_COMPLEX, 4, color_temp, 10, 3)
                cv2.namedWindow(self.window, cv2.WND_PROP_FULLSCREEN)
                cv2.setWindowProperty(self.window, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                cv2.imshow(self.window, constant)

def imadjust(image, newRange = (0,100), oldRange=(0,255)):
    """
        More detail about formula : https://en.wikipedia.org/wiki/Normalization_(image_processing)
        ----
        image : array
        newRange : nehttps://github.com/pytorch/visionw range of value
        Example : newRange = [0,1]
    """
    thers = 38.5
    Min = np.min(image)
    Max = np.max(image)
    newMin = newRange[0]
    if newRange[1]>thers:
        newMax = thers
    else:
        newMax = newRange[1]
    temp = (newMax - newMin) / float(Max - Min)
    image = ((image - Min) * temp + newMin)
    return image 

def rescale_frame(frame, percent=100):
    width = int(frame.shape[1] * percent/ 100)
    height = int(frame.shape[0] * percent/ 100)
    dim = (width, height)
    return cv2.resize(frame, dim, interpolation =cv2.INTER_AREA)

class Camera(object):
        def __init__(self, src=0, ROI=((0,-1),(0,-1)) ):
                self.src = src
                self.ROI = ROI
                self.capture = cv2.VideoCapture(self.src)
                self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 2)
                self.frame = cv2.imread("icon/init.jpg")
                # X = desired FPS
                self.FPS = 1/30
                self.FPS_MS = int(self.FPS * 1000)

                self.thread_video = Thread(target=self.update_video, args=())
                self.thread_video.daemon = True
                self.thread_video.start()

                self.model = load_pytorch_model('models/model360.pth')

                feature_map_sizes = [[45, 45], [23, 23], [12, 12], [6, 6], [4, 4]]
                anchor_sizes = [[0.04, 0.056], [0.08, 0.11], [0.16, 0.22], [0.32, 0.45], [0.64, 0.72]]
                anchor_ratios = [[1, 0.62, 0.42]] * 5
                anchors = generate_anchors(feature_map_sizes, anchor_sizes, anchor_ratios)
                self.anchors_exp = np.expand_dims(anchors, axis=0)
                self.class_id = None
                self.thread_detecion = Thread(target=self.inference, args=())
                self.thread_detecion.daemon = True
                self.thread_detecion.start()

        def update_video(self):
                while True:
                        if self.capture.isOpened():
                                (self.status, self.frame) = self.capture.read()
                                self.frame = self.frame[self.ROI[0][0]:self.ROI[0][1], self.ROI[1][0]:self.ROI[1][1], : ]
                                
                        time.sleep(self.FPS)

        def reset(self):
                cv2.destroyAllWindows()
                cv2.waitKey(self.FPS_MS)
                self.capture = cv2.VideoCapture(self.src)
                self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 2)
                (self.status, self.frame) = self.capture.read()
                self.frame = self.frame[self.ROI[0][0]:self.ROI[0][1], self.ROI[1][0]:self.ROI[1][1], : ]

        def show_frame(self,name='frame'):
                cv2.imshow(name, self.frame)
                cv2.waitKey(self.FPS_MS)

        def inference(self,conf_thresh=0.5,iou_thresh=0.4,target_shape=(360,360)):
            self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            height, width, _ = self.frame.shape
            image_resized = cv2.resize(self.frame, target_shape)
            image_np = image_resized / 255.0  
            image_exp = np.expand_dims(image_np, axis=0)

            image_transposed = image_exp.transpose((0, 3, 1, 2))
            #print(torch.cuda.is_available())
            y_bboxes_output, y_cls_output = pytorch_inference(self.model, image_transposed)
            # remove the batch dimension, for batch is always 1 for inference.
            y_bboxes = decode_bbox(self.anchors_exp, y_bboxes_output)[0]
            y_cls = y_cls_output[0]
            # To speed up, do single class NMS, not multiple classes NMS.
            bbox_max_scores = np.max(y_cls, axis=1)
            bbox_max_score_classes = np.argmax(y_cls, axis=1)

            # keep_idx is the alive bounding box after nms.
            keep_idxs = single_class_non_max_suppression(y_bboxes,
                                                         bbox_max_scores,
                                                         conf_thresh=conf_thresh,
                                                         iou_thresh=iou_thresh,
                                                         )

            for idx in keep_idxs:
                self.class_id = (bbox_max_score_classes[idx])
                bbox = y_bboxes[idx]
                # clip the coordinate, avoid the value exceed the image boundary.
                self.xmin = max(0, int(bbox[0] * width))
                self.ymin = max(0, int(bbox[1] * height))
                self.xmax = min(int(bbox[2] * width), width)
                self.ymax = min(int(bbox[3] * height), height)

            return 1

        def reset_rect(self):
                self.xmin = 0
                self.xmax = 0
                self.ymin = 0
                self.ymax = 0
                self.class_id = None
                return 0

class Audio(object):
    def __init__(self, audioname = 'Merci_mask.wav', chunk = 1024  ):
        pygame.init()
        self.sound = pygame.mixer.Sound(audioname)

        self.thread_audio = Thread(target=self.update_audio, args=())
        self.thread_audio.daemon = True
        self.thread_audio.start()
 
    def update_audio(self):
                if self.sound.get_length is not None:
                        print("Play sound !")
    def play_audio(self):
        self.sound.play()        

class Temperature(object):
        def __init__(self, IP="http://169.254.61.84:80"):
                self.IP = IP
                self.username = 'admin'
                self.password = 'vision29'
                self.range_temp = requests.get(url=self.IP+"/ISAPI/Thermal/channels/2/thermometry/1/rulesTemperatureInfo?format=json", auth=HTTPDigestAuth(self.username,self.password )).json()

                self.thread_temperature = Thread(target=self.update_temperature, args=())
                self.thread_temperature.daemon = True
                self.thread_temperature.start()

        def update_temperature(self):
                if self.range_temp is not None:
                        print("Get temperature !")

        def get_temp(self):
                self.range_temp = requests.get(url=self.IP+"/ISAPI/Thermal/channels/2/thermometry/1/rulesTemperatureInfo?format=json", auth=HTTPDigestAuth(self.username,self.password )).json()
                self.max_temp = self.range_temp['ThermometryRulesTemperatureInfoList']['ThermometryRulesTemperatureInfo'][0]['maxTemperature']
                self.min_temp = self.range_temp['ThermometryRulesTemperatureInfoList']['ThermometryRulesTemperatureInfo'][0]['minTemperature']
       
if __name__ == '__main__': 
    #ROI_camera = ((105,975), (330,1510))                        # Original: 1920*1080
    #ROI_thermal = ((0,-1), (0,-1))                              # Original: 1208*720
   
    ROI_camera = ((305,875), (530,1310))                        # Original: 1920*1080
    ROI_thermal = ((200,-100), (200,-200))  

    threaded_camera = Camera("rtsp://admin:vision29@169.254.61.84/Streaming/channels/101", ROI_camera)
    threaded_thermal = Camera("rtsp://admin:vision29@169.254.61.84/Streaming/channels/201", ROI_thermal)
    threaded_audio = Audio('audio/Merci_mask.wav')
    threaded_info = show_info()
    threaded_temp = Temperature()

    # Parametres
    play_audio = True
    c_no_detect = 0
    c_detect_mask = 0
    c_detect_nomask = 0    
    offset_time = 1.2
    time.sleep(10)
    debut= time.time()

    while True:
        try:
                threaded_camera.inference()
                threaded_temp.get_temp()
                thermal_frame = imadjust(threaded_thermal.frame, newRange = (threaded_temp.min_temp,threaded_temp.max_temp))
                thermal_frame = cv2.resize(thermal_frame, (threaded_camera.frame.shape[1], threaded_camera.frame.shape[0]))

                if threaded_camera.class_id is not None:
                        if threaded_camera.class_id ==0:
                                c_detect_mask +=1
                        else:
                                c_detect_nomask +=1
                        window_y = threaded_camera.ymax-threaded_camera.ymin
                        window_x = threaded_camera.xmax-threaded_camera.xmin
                        thermal_frame = thermal_frame[ threaded_camera.ymin+int(window_y*0.1): threaded_camera.ymin+int(window_y*0.4), threaded_camera.xmin+int(window_x*0.1) : threaded_camera.xmin+int(window_x*0.9), :]
                        temperature = np.round(np.max(thermal_frame),1)
                        threaded_camera.reset_rect()
                else:
                        c_no_detect +=1
                #cv2.imshow('',thermal_frame)
                #cv2.waitKey(threaded_camera.FPS_MS)
                #threaded_camera.show_frame()
                fin = time.time() - debut
                if fin > offset_time:
                        if c_detect_nomask > c_detect_mask and c_detect_nomask > c_no_detect:
                                if play_audio:
                                        threaded_audio.play_audio()
                                        play_audio = False

                                threaded_info.detect(temperature = temperature,mask = False)
                        elif c_detect_mask > c_detect_nomask and c_detect_mask > c_no_detect:
                                threaded_info.detect(temperature = temperature,mask = True)
                                play_audio = True
                        elif c_no_detect > c_detect_nomask and c_no_detect > c_detect_mask:
                                threaded_info.query()
                                play_audio = True
                        cv2.waitKey(threaded_camera.FPS_MS)
                        debut= time.time()
                        c_no_detect = 0
                        c_detect_mask = 0
                        c_detect_nomask = 0  
        except :
                pass

        #print(c_no_detect, c_detect_mask, c_detect_nomask,':',threaded_temp.min_temp, threaded_temp.max_temp )
