from picamera import PiCamera
from time import sleep
import subprocess
from gpiozero import Button

button = Button(17)
camera = PiCamera()
while True:
    button.wait_for_press()
    camera.capture("/home/pi/Desktop/image.jpg")
    subprocess.call(['java', '-jar', '/home/pi/Desktop/photo.jar'])
    subprocess.call(['java','-jar','/home/pi/Desktop/photonotification.jar'])
