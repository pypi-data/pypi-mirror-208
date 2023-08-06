# -*- coding: utf-8 -*-

#
# Simple Python test program to use the RedRatHub.
#
# Ethan Johnson, David Blight, Chris Dodge - RedRat Ltd.
#


import VSautomatic.RedRatHub
import os
import time
from VSautomatic.RedRatHub import Client

log_file_path = os.path.realpath(os.path.dirname(os.path.dirname(__file__)) + '//VSautomatic')



class DEV_REDRAT(object):

    def __init__(self,test_pc_ip,redRat_Name,redRatDataset):
        self.test_pc_ip = test_pc_ip
        self.redRat_Name = redRat_Name
        self.redRatDataset = redRatDataset

    def IR_GEN(self,IRMessage,PauseTimer):
                
        print('You are using %s redrat and %s.xml dataset on %s test PC!'%(self.redRat_Name, self.redRatDataset, self.test_pc_ip))
        
        client = Client()
        
        # Connect to the RedRatHub
        client.OpenSocket(self.test_pc_ip, 40000)

        # Send some IR signals

        client.SendMessage('name="' + self.redRat_Name + '" dataset="'+ self.redRatDataset+ '" signal="' + IRMessage + '" output="12:10"')
        print("Sent signal*\n")
        time.sleep(PauseTimer)



        # List the datasets known by the hub
        print("List of datasets:")
        list = client.ReadData('hubquery="list datasets"')
        print('{}'.format(list))

        client.CloseSocket()
        print("Finished.")

if __name__ == '__main__':
    RedRat=DEV_REDRAT()
    RedRat.IR_GEN('menu',2)
