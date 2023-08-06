# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 15:16:13 2018

@author: yongsongzhu
"""

# -*- coding: utf-8 -*-


import sys
import threading
import time
import serial
import serial.tools.list_ports
import copy


class SigmaSerial(object):
    def __init__(self):
        self.my_serial = None
        self.port_name_list = []  
        self.port_name = ''
        self.autodetect()
    
    def isOpen(self):        
        if not self.my_serial is None:
            return self.my_serial.isOpen()
        else:
            return False
    
    def open(self, port_name=None, baudrate=115200, rtscts=False,stopbits=1):
        if not self.my_serial is None:
            if self.my_serial.isOpen():
                print("Serial has been started, stop it firstly\n")
                self.my_serial.close()
                
        if port_name is None:
            # print(len(self.port_name_list))
            if len(self.port_name_list) == 0:
                self.autodetect()
            self.port_name = self.port_name_list[1]
        else:
            self.port_name = port_name
            
        if not self.port_name.startswith('COM'):
            print('Port name is wrong', self.port_name)
            return False

        self.my_serial = serial.Serial()
        self.my_serial.port = self.port_name
        self.my_serial.baudrate = baudrate
        self.my_serial.rtscts = rtscts
        self.my_serial.bytesize = serial.EIGHTBITS
        self.my_serial.parity = serial.PARITY_NONE
        if stopbits == 1:
            self.my_serial.stopbits = serial.STOPBITS_ONE
        else:
            self.my_serial.stopbits = serial.STOPBITS_TWO
        self.my_serial.open()
        print(self.port_name)
        print(self.my_serial.isOpen())
        if self.my_serial.isOpen():
            return True
        else:
            return False

    def readlines(self):
        try:
            if self.my_serial.isOpen():
                return self.my_serial.read_all()
        except Exception as ex:
            print(ex)

        return ''
    
    def writes(self, cmd, *args, **kw):
        '''
        args = ('a', 'b')
        kw = {'dict':99}
        '''
        # print(cmd)
        msg = copy.deepcopy(cmd)
        for i in range(len(args)):
            msg += ' ' + args[i]
            print(args)
        print("Write Cmd:", msg)

        
        # return self.my_serial.write(msg + b'\n')
        return self.my_serial.write(msg.encode('UTF-8') + b'\n')
        # return self.my_serial.write(msg.encode('UTF-8') + '\n')
        # return self.my_serial.write(msg.encode('UTF-8') + '\n')

    def close(self):
        if self.my_serial.isOpen():
            self.my_serial.close()
    
    def autodetect(self):
        serial_list = list(serial.tools.list_ports.comports())
        #print serial_list
        if serial_list:	
            self.port_name_list = []			
            for i in range(0, len(serial_list)):
                portname = list(serial_list[i])
                self.port_name_list.append(str(portname[0]))
            print("Available serial port list: ", self.port_name_list)
