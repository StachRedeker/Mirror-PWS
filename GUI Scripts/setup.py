import pip
import sys
import subprocess

def install_if_not(package):
    try:
        __import__(package)
        print("~ Package '{0}' was already installed".format(package))
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print("+ Installed '{0}'".format(package))
    
install_if_not("yfinance")
install_if_not("forex_python") 
install_if_not("pytz")
install_if_not("numpy") 
install_if_not("datetime")
install_if_not("json") 
install_if_not("pytz")
