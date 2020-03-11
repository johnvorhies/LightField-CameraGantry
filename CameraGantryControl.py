import RPi.GPIO as GPIO
import time
from operator import xor
import gphoto2 as gp
import os

class gantryControl:
    #-------------- I/O Pin Masks -----------------
    LIMIT_TOP = 17
    LIMIT_BOTTOM = 4
    LIMIT_RIGHT = 27
    LIMIT_LEFT = 22
    LIMIT_SWITCHES = (LIMIT_TOP, LIMIT_BOTTOM, LIMIT_RIGHT, LIMIT_LEFT)
    STEP_X = 20
    DIRECTION_X = 21
    STEP_Y = 24
    DIRECTION_Y = 25
    i1 = 12
    i2 = 16
    ms2 = 1
    ms1 = 7
    #------------- Stepper Motor Direction --------
    motorDirectionX = GPIO.HIGH # Left
    motorDirectionY = GPIO.HIGH # Down
    
    def __init__(self,CURRENT_LIMIT,RESOLUTION):
        self.CURRENT_LIMIT = CURRENT_LIMIT
        self.RESOLUTION = RESOLUTION
        self.GPIOSetup()
    
    def GPIOSetup(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.LIMIT_SWITCHES, GPIO.IN, GPIO.PUD_UP)
        
        # Stepper Motor Control
        step = (self.STEP_X,self.STEP_Y)
        GPIO.setup(step, GPIO.OUT)
        GPIO.output(step, GPIO.LOW)
        
        # Stepper Motor Direction
        direction = (self.DIRECTION_X,self.DIRECTION_Y)
        directionControl = (self.motorDirectionX,self.motorDirectionY)
        GPIO.setup(direction, GPIO.OUT)
        GPIO.output(direction, directionControl)
        
        # Current Control
        CURRENT_CONTROL = (self.i1,self.i2)
        GPIO.setup(CURRENT_CONTROL, GPIO.OUT)
        GPIO.output(CURRENT_CONTROL, self.CURRENT_LIMIT)

        # microstepping Control
        MICRO_STEP = (self.ms1,self.ms2)
        GPIO.setup(MICRO_STEP, GPIO.OUT)
        GPIO.output(MICRO_STEP, self.RESOLUTION)
        
    def stepPulse(self,step):
        PULSE_LENGTH = 1/2300
        GPIO.output(step,GPIO.HIGH)
        time.sleep(PULSE_LENGTH)
        GPIO.output(step,GPIO.LOW)
        time.sleep(PULSE_LENGTH)
    
    def moveMotor(self,step,distance):
        # distance in millimeters
        STEPS_REV = 200     # Motor specs
        STEP_RES = 8        # microstepping resolution
        BELT_PITCH = 2      # Belt specs, mm
        NUM_TEETH = 20      # Pulley specs
        stepsPerMM = (STEPS_REV*STEP_RES)/(BELT_PITCH*NUM_TEETH)
        
        stepsToTake = stepsPerMM*distance
        for i in range(int(stepsToTake)):
            self.stepPulse(step)
        
    def switchDetect(self,LIMIT_SWITCHES):
        for switch in self.LIMIT_SWITCHES:
            if GPIO.event_detected(switch):
                print('limit detected: ', switch)
                
    def reverseDirectionX(self):
        self.motorDirectionX = int(xor(bool(self.motorDirectionX),bool(1)))
        GPIO.output(self.DIRECTION_X,self.motorDirectionX)
        
    def reverseDirectionY(self):
        self.motorDirectionY = int(xor(bool(self.motorDirectionY),bool(1)))
        GPIO.output(self.DIRECTION_Y,self.motorDirectionY)
        
    def backUpX(self):
        self.reverseDirectionX()
        for i in range(11500):
            self.stepPulse(self.STEP_X)
            
    def backUpY(self):
        self.reverseDirectionY()
        for i in range(800):
            self.stepPulse(self.STEP_Y)
    
    def initializeToCorner(self):
        while(GPIO.input(self.LIMIT_BOTTOM) == GPIO.LOW):
            self.stepPulse(self.STEP_Y)
        self.backUpY()
        while(GPIO.input(self.LIMIT_LEFT) == GPIO.LOW):
            self.stepPulse(self.STEP_X)
        self.backUpX()
            
    def returnToLeft(self):
        self.reverseDirectionX()
        while(GPIO.input(self.LIMIT_LEFT) == GPIO.LOW):
            self.stepPulse(self.STEP_X)
        self.backUpX()
    
#-----------------Functions-----------------------------
        
def captureImage(camera):
    file_path = camera.capture(gp.GP_CAPTURE_IMAGE)
    target = os.path.join('/media/pi/BDBE-A787/Light_Field_Images', file_path.name)
    camera_file = camera.file_get(
        file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL)
    camera_file.save(target)
    
def captureLightFieldImage(LF_SIZE,LF_SPACING,gantryControl,camera):
    # LF_SIZE: size of (s,t) plane is (LF_SIZE,LF_SIZE)
    # LF_SPACING: resolution of (s,t) in millimeters
    gantryControl.initializeToCorner()
    for nt in range(LF_SIZE):
        time.sleep(2)
        for ns in range(LF_SIZE):
            captureImage(camera)
            gantryControl.moveMotor(gantryControl.STEP_X,LF_SPACING)
            time.sleep(2)
        gantryControl.returnToLeft()
        time.sleep(1)
        gantryControl.moveMotor(gantryControl.STEP_Y,LF_SPACING)
    gantryControl.reverseDirectionY()
    gantryControl.reverseDirectionX()
    gantryControl.initializeToCorner()
      
def hitFourCorners(gantryControl):
    gantryControl.initializeToCorner()
    while(GPIO.input(gantryControl.LIMIT_TOP) == GPIO.LOW):
        gantryControl.stepPulse(gantryControl.STEP_Y)
    gantryControl.backUpY()
    
    while(GPIO.input(gantryControl.LIMIT_RIGHT) == GPIO.LOW):
        gantryControl.stepPulse(gantryControl.STEP_X)
    gantryControl.backUpX()
    
    while(GPIO.input(gantryControl.LIMIT_BOTTOM) == GPIO.LOW):
        gantryControl.stepPulse(gantryControl.STEP_Y)
    gantryControl.backUpY()
    
    while(GPIO.input(gantryControl.LIMIT_LEFT) == GPIO.LOW):
        gantryControl.stepPulse(gantryControl.STEP_X)
    gantryControl.backUpX()

def testMotorX(gantryControl):
    for j in range(10):
        for i in range(1600):
            gantryControl.stepPulse(gantryControl.STEP_X)
        time.sleep(1)
        gantryControl.reverseDirectionX()

def testMotorY(gantryControl):
    for j in range(10):
        for i in range(300):
            gantryControl.stepPulse(gantryControl.STEP_Y)
        time.sleep(1)
        gantryControl.reverseDirectionY()

#-------------- Initializations ------------------------
CURRENT_LIMIT = {'0.5A':(1,1),
                 '1A':(0,1),
                 '1.5A':(1,0),
                 '2A':(0,0)}

RESOLUTION = {'Full':(0,0),
              '1/2':(1,0),
              '1/4':(0,1),
              '1/8':(1,1)}

gantryControl = gantryControl(CURRENT_LIMIT['2A'],RESOLUTION['1/8'])

# Threaded callback setup
for switch in gantryControl.LIMIT_SWITCHES:
    GPIO.add_event_detect(switch, GPIO.RISING, callback=gantryControl.switchDetect, bouncetime=2000)

# Camera Setup
camera = gp.Camera()
camera.init()

captureLightFieldImage(13,10,gantryControl,camera)


