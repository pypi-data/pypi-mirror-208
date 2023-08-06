import subprocess
import os

def asa_conf():
    asa1_home = os.environ.get('ASA_HOME')   # 使用环境变量的方式
    path = asa1_home+'/conf.ini'
    subprocess.Popen(['notepad.exe', path])