# -*- coding: utf-8 -*-
"""
Created on Mon Sep 03 15:32:13 2018

"""
import threading
import time

# -*- coding: utf-8 -*-

import cv2
# from memory_profiler import profile

class CameraCapture(object):
    def __init__(self):
        self.my_camera = None
        self.my_camera_fps = 0
        self.my_camera_resolution=()
        # self.my_camera_lock = threading.Lock()

    def isOpen(self):        
        if not self.my_camera is None:
            return self.my_camera.isOpened()
        else:
            return False

    def open(self):
        self.my_camera=cv2.VideoCapture(0,cv2.CAP_DSHOW)
        self.my_camera_fps= self.my_camera.get(cv2.CAP_PROP_FPS)
        print('camera fps:',self.my_camera_fps)
        self.my_camera_resolution=(int(self.my_camera.get(cv2.CAP_PROP_FRAME_WIDTH)),int(self.my_camera.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        print('camera resolution:',self.my_camera_resolution)

    def imageCapture(self,picName,frameNum):
        print("start capture image")
        for i in range(int(frameNum)):
            isSuccess,frame = self.my_camera.read()
            if isSuccess:
                cv2.imwrite(picName+'_'+str(i+1)+'.jpg', frame)
        print("stop capture image")

    def videoCapture(self,vidName,duration):
        print("start capture video")
        start_time = time.time()
        # self.my_camera_lock.acquire()
        self.my_camera.set(3,640)
        self.my_camera.set(4,480)
        self.my_camera.set(1,10.0)
        # fourcc=cv2.cv.CV_FOURCC('m','p','4','v')
        fourcc=cv2.VideoWriter_fourcc('m','p','4','v')
        # fourccs = cv2.imwrite('RGB.jpg', self.flip_hv)
        out = cv2.VideoWriter(vidName+'.mp4',fourcc,24,(640,480))
        print(vidName)
        print(self.my_camera.isOpened())
        
        print("Start camera")
        framenumber=int(duration)*24
        for n in range(framenumber):
            ret,frame = self.my_camera.read()
            if ret == True:
                out.write(frame)
            else:
                break

        print("Closed camera")
        self.my_camera.release()
        out.release()
        end_time = time.time()
        run_time = end_time - start_time
        print(run_time)
        print("stop capture video")
        # self.my_camera_lock.release()

    def close(self):
        if self.my_camera.isOpened():
            self.my_camera.release()


if __name__ == "__main__":
    
    cap = CameraCapture()
    cap.open()
    print(cap.isOpen())
    cap.imageCapture('cherry_test',3)
    cap.videoCapture('cherry_test',5)
    cap.close()
    #cap.videoCapture('cherry_video',1)


