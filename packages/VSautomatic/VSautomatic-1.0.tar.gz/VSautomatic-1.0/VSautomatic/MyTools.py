import os
import sys
import threading
import time
import copy
import serial
import serial.tools.list_ports
from VSautomatic.my_serial import SigmaSerial
from VSautomatic.MyCamera import CameraCapture
from VSautomatic.ReSTTerminal import restterminal
from VSautomatic.RedRatHubS import RedRatHubCmdSetUp
from VSautomatic.MyRedRat import DEV_REDRAT
from .deco import keyword

log_file_path = os.path.realpath(os.path.dirname(os.path.dirname(__file__)) + '//VSautomatic')
Auth_Token = log_file_path + '\Auth_Token.txt'

class MyTools(object):

    def __init__(self):
        self.my_serial = None
        self.my_camera = None
        self.my_rest = None
        self.RedRatS = None
        self.RedRatC = None

    
    # COM-Serial-Start
    def serial_start(self, portname):
        '''
        portname:COMx
        | `Serial Start`    | COM3 |
        '''
        if self.my_serial is None:
            self.my_serial = SigmaSerial()
        try:
            self.my_serial.open(portname)
            if self.my_serial.isOpen():
                self.alive = True
                # self.thread_read = threading.Thread(target=self.serial_reader)
                # self.thread_read.setDaemon(True)
                # self.thread_read.start()
                return True
            else:
                return False
        except Exception as e:
            return False

    def serial_reader(self):
        '''
        Example:
        | ${a}               | `Serial Reader` |
        | Log                | ${a}            |
        | `Open Connection`  | my.server.com   |
        | `Login`            | johndoe         | secretpasswd |
        | `Get File`         | results.txt     | /tmp         |
        | `Close Connection` |
        | # Do something with /tmp/results.txt                |
        '''
        try:
            data = self.my_serial.readlines()
            if len(data) > 1:
                print(data)
                return data
                # logfile = open('.\\Logs\\DUT_log.txt', 'a+')
                # logfile.write(data.decode('utf-8'))
                # logfile.flush()
                # logfile.close()
        except Exception as e:
            print(e)

    def serial_writer(self, command):
        self.my_serial.writes(command)
        


    def serial_stop(self):
        if not self.my_serial is None:
            self.alive = False
            if self.my_serial.isOpen():
                self.my_serial.close()
    
    # COM-Serial-End
    # ====================================================================================================================================
    # Rest-Start
    def rest_pair(self,ip):
        self.my_rest = restterminal(ip)
        self.auth_token = self.my_rest.sshpair()
        fw = open(Auth_Token, "w")
        fw.write(self.auth_token)
        fw.close()

    def rest_send(self,command):
        fr = open(Auth_Token, "r")
        self.read_auth_token = fr.readline().strip('\n')
        fr.close()
        if self.my_rest is None:
            self.my_rest = restterminal()

        self.my_rest.read_dictionary()
        restValue = self.my_rest.parse_command(command, self.read_auth_token)
        print('restValue:{}'.format(restValue))
        time.sleep(3)
        self.my_rest.parse_command("restlog", self.read_auth_token)

    # Rest-End
    # ====================================================================================================================================
    # Camera-Start
    def camera_open(self):
        if self.my_camera is None:
            self.my_camera = CameraCapture()
        try:
            self.my_camera.open()
            if self.my_camera.isOpen():
                self.alive = True
                # self.thread_read = threading.Thread(target=self.serial_reader)
                # self.thread_read.setDaemon(True)
                # self.thread_read.start()
                return True
            else:
                return False
        except Exception as e:
            return False
            

    def camera_imageCapture(self,picName,frameNum):
        self.my_camera.imageCapture(picName,frameNum)

    def camera_videoCapture(self,vidName,duration):
        self.my_camera.videoCapture(vidName,duration)


    def camera_stop(self):
        if not self.my_camera is None:
            self.alive = False
            if self.my_camera.isOpen():
                self.my_camera.close()

    # Camera-End
    # ====================================================================================================================================
    # RedRat_Start
    def RedRat_Run_Server(self,RedRatdate):
        self.RedRatS = RedRatHubCmdSetUp(RedRatdate)
        self.RedRatS.run()
        
    def RedRat_Kill_Server(self):
        self.RedRatS.kill()

    def RedRat_Client(self,test_pc_ip,redRat_Name,redRatDataset):
        self.RedRatC = DEV_REDRAT(test_pc_ip,redRat_Name,redRatDataset)

    def RedRat_Client_Send(self,IRMessage,PauseTimer):
        self.RedRatC.IR_GEN(IRMessage,int(PauseTimer))
    # RedRat_End
