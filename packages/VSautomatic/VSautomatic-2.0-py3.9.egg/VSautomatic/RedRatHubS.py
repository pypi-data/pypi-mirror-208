
import subprocess
from time import sleep
import os

log_file_path = os.path.realpath(os.path.dirname(os.path.dirname(__file__)) + '//VSautomatic')




class RedRatHubCmdSetUp():

    def __init__(self,RedRatdate):
        self.RedRatdate = RedRatdate

    def run(self):
        try:
            # print(log_file_path + '\RedRatHub-V4.27\RedRatHubCmd '+ self.RedRatdate + '.xml')
            subprocess.Popen(log_file_path + '\RedRatHubCmd  ' + log_file_path + '\\' + self.RedRatdate + '.xml')
            print("RedRatHubCmd server boot up")

        except Exception as e:
            print("Error: 无法启动进程")
            print(repr(e))


    def kill(self):
        try:
            subprocess.Popen('taskkill /F /im RedRatHubCmd.exe')
            print("kill RedRatHubCmd server")

        except Exception as e:
            print("Error: 无法启动进程")
            print(repr(e))


if __name__ == '__main__':
    RedRat = RedRatHubCmdSetUp()
    RedRat.run()
    sleep(60)
    RedRat.kill()