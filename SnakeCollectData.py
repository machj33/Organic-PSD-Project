# Test G Code file
import serial
import time
from threading import Event
from pymeasure.instruments.agilent import Agilent4156
from pymeasure.instruments import list_resources
import numpy as np

BAUD_RATE = 115200

# One contact per run or four contacts per run
single = False

# Change to the port used in Candle
GRBL_port_path = 'COM4'

# 4155-C connection
smu = Agilent4156("GPIB0::2::INSTR", read_termination = '\n', write_termination = '\n',
                  timeout=None)
smu.reset()
smu.configure("simple_read.json")
smu.analyzer_mode = "SWEEP"
smu.integration_time = "LONG"
if single:
    smu.save(['I1'])
else:
    smu.save(['I1', 'I2', 'I3', 'I4'])

# NPL Cycles (2 to 100) (.0333 to 1.666 seconds)
npl = 7
smu.write(f":PAGE:MEAS:MSET:ITIM:LONG {npl}")  

# Starting at "Top" or "Bottom"
startAt = "Top"

# Discrete measurement points
xPoints = 6
yPoints = 6

# Length of usable area in mm
xLength = 35
yLength = 35

# Distance between each measurement point
xDist = xLength / (xPoints - 1)
yDist = yLength / (yPoints - 1)

# Speed of movements
speed = 500

# Current Data
numMeasurements = 4
currentMeasurements = np.zeros((numMeasurements, xPoints, yPoints))
darkCurrent = []

# Should be useless right now, may be utilized if gcode files are used in the future
def remove_comment(string):
    if (string.find(';') == -1):
        return string
    else:
        return string[:string.index(';')]


def remove_eol_chars(string):
    # removed \n or traling spaces
    return string.strip()

# Not sure this is necessary with our setup, but works currently
def send_wake_up(ser):
    # Wake up
    # Hit enter a few times to wake the Printrbot
    ser.write(str.encode("\r\n\r\n"))
    time.sleep(2)   # Wait for Printrbot to initialize
    ser.flushInput()  # Flush startup text in serial input

def set_speed(ser,mmpm):
    command = str.encode('F' + str(mmpm) + '\n') # Set speed using F command, mmpm must be an int
    ser.write(command)  # Send g-code

# "Center" to top left of the detector
def center(ser):
    #Define later
    temp = 1

def move(ser, x, z = 0):
    line = "G1 X" + str(x) + " Z" + str(z) + "\n"
    print("Executing line: " + line)
    command = str.encode(line)
    ser.write(command)
    wait_for_movement_completion(ser,line)
    grbl_out = ser.readline()

# Some sort of reading
def read(instr):
    instr.measure()
    start_of_data = time.time()
    data = instr.get_data()
    end_of_data = time.time()
    print('Get Data Time:')
    print(end_of_data - start_of_data)
    return data

# Not sure why this does exactly what it does
def wait_for_movement_completion(ser,cleaned_line):

    Event().wait(0.01)

    # Any '$' line can be skipped? Maybe to cut down on the idle counter?
    # Maybe the idle_counter is only for movements, but then $H might also be a movement
    if cleaned_line != '$X' or '$$':

        idle_counter = 0

        while True:

            # Event().wait(0.01)
            ser.reset_input_buffer()
            command = str.encode('?' + '\n') # Probe status
            ser.write(command)
            grbl_out = ser.readline() 
            grbl_response = grbl_out.strip().decode('utf-8')

            if grbl_response != 'ok':

                if grbl_response.find('Idle') > 0:
                    idle_counter += 1

            # Make sure the machine is idle for 10 cycles of code?
            if idle_counter > 10:
                break
    return

def snake_pass(GRBL_port_path):
    global darkCurrent
    with serial.Serial(GRBL_port_path, BAUD_RATE) as ser:
        send_wake_up(ser)
        ser.write(str.encode('G21')) # Metric system
        ser.write(str.encode('G91')) # Relative movement mode
        set_speed(ser, speed)
        # center(ser)

        darkCurrent = read(smu)

        input("Turn on the laser. Press enter to continue")
        
        # Right is '-1' and left is '1'
        xDirection = -1
        yDirection = -1

        # From the left corner of the PSD
        for j in range(yPoints):
            flipRows = 1
            # Starting at the top, you want to fill in the array from the top,
            # travel downwards instead of upwards, and flip even rows if yPoints
            # is even, and odd rows if yPoints is odd. Starting at the bottom,
            # you don't have to worry about this.
            if startAt == "Top":
                j = yPoints - 1 - j
                yDirection = 1
                flipRows = yPoints % 2
            for i in range(xPoints):
                data = read(smu)
                currentMeasurements[0, j, i] = data['I1'].iloc[0]
                currentMeasurements[1, j, i] = data['I2'].iloc[0]
                currentMeasurements[2, j, i] = data['I3'].iloc[0]
                currentMeasurements[3, j, i] = data['I4'].iloc[0]
                move(ser, xDirection * xDist)
            # This flips every other row to account for the snake path, defined by flipRows
            if j % 2 == flipRows:
                currentMeasurements[0, j, :] = np.flip(currentMeasurements[0, j, :])
                currentMeasurements[1, j, :] = np.flip(currentMeasurements[1, j, :])
                currentMeasurements[2, j, :] = np.flip(currentMeasurements[2, j, :])
                currentMeasurements[3, j, :] = np.flip(currentMeasurements[3, j, :])
            xDirection *= -1
            move(ser, xDirection * xDist, yDirection * yDist)
        move(ser, xLength/2 + xDirection * xLength/2, -1 * yDirection * (yLength + yDist))
        move(ser, 5)

def snake_pass_single(GRBL_port_path):
    global darkCurrent
    with serial.Serial(GRBL_port_path, BAUD_RATE) as ser:
        send_wake_up(ser)
        ser.write(str.encode('G21')) # Metric system
        ser.write(str.encode('G91')) # Relative movement mode
        set_speed(ser, speed)
        # center(ser)

        smu.measure()
        darkCurrent = smu.get_data()

        input("Turn on the laser. Press enter to continue")

        # Set up for the loop
        move(ser, 5)

        for k in range(numMeasurements):
            # Put the laser back on the device
            move(ser, -5)

            # Right is '-1' and left is '1'
            xDirection = -1
            yDirection = -1
            
            # From the left corner of the PSD
            for j in range(yPoints):
                flipRows = 1
                # Starting at the top, you want to fill in the array from the top,
                # travel downwards instead of upwards, and flip even rows if yPoints
                # is even, and odd rows if yPoints is odd. Starting at the bottom,
                # you don't have to worry about this.
                if startAt == "Top":
                    j = yPoints - 1 - j
                    yDirection = 1
                    flipRows = yPoints % 2
                for i in range(xPoints):
                    start = time.time()
                    smu.measure()
                    start_of_data = time.time()
                    data = smu.get_data()
                    end_of_data = time.time()
                    currentMeasurements[k, j, i] = data['I1'].iloc[0]
                    end = time.time()
                    print('Total Time:')
                    print(end - start)
                    print('Get Data Time:')
                    print(end_of_data - start_of_data)
                    move(ser, xDirection * xDist)
                # This flips every other row to account for the snake path, as defined by flipRows
                if j % 2 == flipRows:
                    currentMeasurements[k, j, :] = np.flip(currentMeasurements[k, j, :])
                xDirection *= -1
                move(ser, xDirection * xDist, yDirection * yDist)
            move(ser, xLength/2 + xDirection * xLength/2, -1 * yDirection * (yLength + yDist))
            move(ser, 5)
            input("Change the wiring. Press enter to continue")

def stream_gcode(GRBL_port_path,gcode_path):
    # with contect opens file/connection and closes it if function(with) scope is left
    with open(gcode_path, "r") as file, serial.Serial(GRBL_port_path, BAUD_RATE) as ser:
        send_wake_up(ser)
        for line in file:
            # cleaning up gcode from file
            cleaned_line = remove_eol_chars(remove_comment(line))
            if cleaned_line:  # checks if string is empty
                print("Sending gcode:" + str(cleaned_line))
                # converts string to byte encoded string and append newline
                command = str.encode(line + '\n')
                ser.write(command)  # Send g-code

                wait_for_movement_completion(ser,cleaned_line)

                grbl_out = ser.readline()  # Wait for response with carriage return
                print(" : " , grbl_out.strip().decode('utf-8'))

                
        
        print('End of gcode') 

gcode_path = 'grbl_test.gcode'
gcode_path_2 = 'gcode/snake.gcode'

print("USB Port: ", GRBL_port_path)

if single:
    snake_pass_single(GRBL_port_path)
else:
    snake_pass(GRBL_port_path)

# stream_gcode(GRBL_port_path,gcode_path_2)
np.save("test_data_LD7.npy", currentMeasurements)
np.save("dark_current_LD7.npy", darkCurrent)
print("Completed")
