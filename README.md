# LightField-CameraGantry
A Python script for controlling a light field camera gantry. The camera gantry is controlled by a Raspberry Pi, which interfaces with a motor control circuit via GPIO pins. This uses the **python-gphoto2** library for controlling the camera, a python binding of **libgphoto2**.

## Classes

### gantryControl
This class provides functions and definitions for interfacing with the motor control circuit via GPIO pins.

#### Definitions
These definitions define the GPIO pins on the Raspberry Pi that connect to the motor control circuit:
* **LIMIT_TOP, LIMIT_BOTTOM, LIMIT_RIGHT, LIMIT_LEFT**: GPIO pins for each limit switch. This script asynchronously monitors the voltage on these GPIO pins to determine if a limit switch has been tripped.
* **STEP_X, STEP_Y**: A pulse width modulation (PWM) signal is sent to these GPIO pins for the MP6500 motor driver chips.
* **DIRECTION_X, DIRECTION_Y**: A high or low voltage is sent to these GPIO pins to change direction of the stepper motors using the MP6500 motor driver chips. A high voltage causes the x-axis motors to move left, and the y-axis motors to move down.
* **i1, i2**: Current limit signals for the MP6500 motor driver chips.
* **ms1, ms2**: Micro-stepping signals for the MP6500 motor driver chips.

#### Functions
##### GPIOSetup(self)
Sets up the GPIO pins from definitions. Sets internal pull-up resistors for limit switches.

#### stepPulse(self,step)
Sends PWM signal to motor drivers to activate the stepper motors. Used internally in **moveMotor**, **backUpX**, **backUpY**.
* **step**: **STEP_X** or **STEP_Y**.

### moveMotor(self,step,distance):
Uses specs of the pulley system to determine a distance in millimeters to move the motors.
* **step**: **STEP_X** or **STEP_Y**.
* **distance**: Distance in millimeters to travel.

### switchDetect(self,LIMIT_SWITCHES):
Prints to output if a limit switch is depressed.
* **LIMIT_SWITCHES**: GPIO pins for each limit switch, **LIMIT_TOP, LIMIT_BOTTOM, LIMIT_RIGHT, LIMIT_LEFT**.

### reverseDirectionX(self):
Reverses the direction of travel for the x-axis motors by altering **DIRECTION_X**.

### reverseDirectionY(self):
Reverses the direction of travel for the y-axis motors by altering **DIRECTION_Y**.

### backUpX(self):
Backs the x-axis motors up when a limit switch is triggered.

### backUpY(self):
Backs the y-axis motors up when a limit switch is triggered.

### initializeToCorner(self):
Returns the camera platform to the bottom-left corner of the camera gantry.

### returnToLeft(self):
Returns the x-axis motor to the far left of the camera gantry.

## Functions
These functions abstract the use of the **gantryControl** class to higher level camera gantry functionality.

### captureImage(camera):
Takes a gphoto2 camera object and sends a signal to capture an image, then stores to an external hard drive. The path in **target** should be changed to the local path of the external hard drive.

### captureLightFieldImage(LF_SIZE,LF_SPACING,gantryControl,camera):
Main function for capturing light field images using the camera gantry.

* **LF_SIZE**: Number of sub-aperture views to be captured. Assumes a square light field image is desired.
* **LF_SPACING**: Spacing in millimeters between sub-aperture views.
* **gantryControl**: An object of the **gantryControl** class.
* **camera**: a gphoto2 camera object

### hitFourCorners(gantryControl):
Used to test the functionality of the camera gantry.

* **gantryControl**: An object of the **gantryControl** class.

### testMotorX(gantryControl):
Tests functionality of the x-axis motors.

* **gantryControl**: An object of the **gantryControl** class.

### testMotorY(gantryControl):
Tests functionality of the y-axis motors.

* **gantryControl**: An object of the **gantryControl** class.




