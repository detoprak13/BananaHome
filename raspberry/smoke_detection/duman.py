import RPi.GPIO as GPIO
import time
import subprocess
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN)
GPIO.setup(7,GPIO.OUT)
GPIO.output(7, True)

try:

    while True:
        subprocess.call(['java', '-jar', '/home/pi/Desktop/smoke.jar', 'yok'])
        if not GPIO.input(4):
            subprocess.call(['java', '-jar', '/home/pi/Desktop/smoke.jar', 'var'])
            subprocess.call(['java','-jar','/home/pi/Desktop/gasnotification.jar'])
            time.sleep(20)
except KeyboardInterrupt:
    GPIO.cleanup()

