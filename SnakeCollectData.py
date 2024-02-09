# Test G Code file
import serial
import time
from threading import Event
from pymeasure.instruments.agilent import Agilent4156
from pymeasure.instruments import list_resources
import numpy as np

BAUD_RATE = 115200

# Change to the port used in Candle
GRBL_port_path = 'COM3'

# 4155-C connection
smu = Agilent4156("GPIB0::2::INSTR", read_termination = '\n', write_termination = '\n',
                  timeout=None)
smu.reset()
smu.configure("Parameter Analyzer/simple_read.json")
smu.analyzer_mode = "SWEEP"
smu.integration_time = "LONG"
smu.save(['I1', 'I2', 'I3', 'I4'])

# NPL Cycles (2 to 100) (.0333 to 1.666 seconds)
npl = 5
smu.write(f":PAGE:MEAS:MSET:ITIM:LONG {npl}")

# Discrete measurement points
xPoints = 6
yPoints = 6

# Length of usable area in mm
xLength = 40
yLength = 40

# Distance between each measurement point
xDist = xLength / (xPoints - 1)
yDist = yLength / (yPoints - 1)

# Speed of movements
speed = 500

# Current Data
numMeasurements = 4
currentMeasurements = np.zeros((numMeasurements, xPoints, yPoints))

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
def read(ser):
    status = smu.measure()
    return smu.get_data()

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
    with serial.Serial(GRBL_port_path, BAUD_RATE) as ser:
        send_wake_up(ser)
        ser.write(str.encode('G21')) # Metric system
        ser.write(str.encode('G91')) # Relative movement mode
        set_speed(ser, speed)
        # center(ser)
        
        # Right is '-1' and left is '1'
        direction = -1

        # From the bottom left of the PSD
        for j in range(yPoints):
            for i in range(xPoints):
                start = time.time()
                status = smu.measure()
                start_of_data = time.time()
                data = smu.get_data()
                end_of_data = time.time()
                currentMeasurements[0, j, i] = data['I1']
                currentMeasurements[1, j, i] = data['I2']
                currentMeasurements[2, j, i] = data['I3']
                currentMeasurements[3, j, i] = data['I4']
                end = time.time()
                print('Total Time:')
                print(end - start)
                print('Get Data Time:')
                print(end_of_data - start_of_data)
                move(ser, direction * xDist)
            if j % 2 == 1:
                currentMeasurements[0, j, :] = np.flip(currentMeasurements[0, j, :])
                currentMeasurements[1, j, :] = np.flip(currentMeasurements[1, j, :])
                currentMeasurements[2, j, :] = np.flip(currentMeasurements[2, j, :])
                currentMeasurements[3, j, :] = np.flip(currentMeasurements[3, j, :])
            direction *= -1
            move(ser, direction * xDist, -1 * yDist)
        move(ser, xLength/2 + direction * xLength/2, yLength + yDist)

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
snake_pass(GRBL_port_path)
# stream_gcode(GRBL_port_path,gcode_path_2)
np.save("test_data.npy", currentMeasurements)
print("Completed")