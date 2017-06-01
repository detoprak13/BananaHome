import RPi.GPIO as GPIO
import time

servo_pin = 17
duty_cycle = 7.5     # Should be the centre for a SG90

# Configure the Pi to use pin names (i.e. BCM) and allocate I/O
GPIO.setmode(GPIO.BCM)
GPIO.setup(servo_pin, GPIO.OUT)

# Create PWM channel on the servo pin with a frequency of 50Hz
pwm_servo = GPIO.PWM(servo_pin, 50)
pwm_servo.start(duty_cycle)

try:
    while True:
        pwm_servo.ChangeDutyCycle(5)
        time.sleep(10)        
        pwm_servo.ChangeDutyCycle(3)
        time.sleep(2)        
            
except KeyboardInterrupt:
    print("CTRL-C: Terminating program.")
finally:
    print("Cleaning up GPIO...")
    GPIO.cleanup()
