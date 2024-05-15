# Organic-PSD-Project
Location for GCode files, SPA measurement scripts, and data analysis. 

The purpose of this repository is primarily to store code needed to execute GCode commands to servo motors, 
obtain current-voltage measurement using an Agilent 4155C semiconductor parameter analyzer, and to 
analyze and display the data obtained from organic position sensitive detectors (PSDs). 

This repository may also be updated to include code to train artificial neural networks trained on obtained 
data to improve the position sensing accuracy of the aforementioned PSDs.

Necessary libraries include -- PyVisa/PyMeasure, TensorFlow, Matplotlib, numpy, etc. More in-depth
instructions can be found in the file StartInstructions.txt

# Future Improvements
Here are a few things that could be improved in the future of this project, relating exclusively to code and
data collection.

1. Automate the alignment of the device
Instead of manually aligning the device, it may be possible to align the devices automatically by reading
where the current drops off the edge of the device. Since current should be 0 when the laser is off of the
device, whenever an appreciable increase in current is detected scanning left to right, you would be able
to determine where the left edge of the device is. This value can be saved, and the process can be repeated
for the top edge or all remaining edges. By aligning based on electrical signals rather than sight, there
should be less human error involved in each scan, as well making it easier to start a new scan.

2. Add a second scan option
In Ryan Veatch's, a dense dataset is simulated to create a training set, and a sparse dataset is generated
to fit in between the dense set. This shouldn't be too difficult to achieve based on the current code. All it would take is to add an option to run the snake pass function again after changing the spacing and staring location of the laser. The hardest part about this will be finding increments and step sizes that don't overlap points. 

3. Determine/Minimize the leakage current
Now, there are slight variances in the voltage from each SMU port, typically at least 0.2 mV difference. This might
be a big factor in the high dark current values at the start of each scan. Can these differences be fixed by using
another device to read, like the Keithley ground source? Is this problem caused by device defects? Is there no fix?
To test how well another device works, you will likely need to learn how to use PyVISA to interact with the devices
using GPIB commands. This may seem daunting at first, but there should be enough already provided in this repository
and online.

4. Investigate the NPL cycles
There is a balance between having quick readings and having accurate readings. As of right now, only 7 NPL cycles
are used to take each point of measurement. The goal is to get the time as short as possible without sacficing
the quality of the data. However, doing a quick test of current readings against NPL cycles, I saw a logarithmic
graph which showed that with more cycles, there were greater signals. If this were shown to be true again, maybe it may be worth it to inccrease the number of NPL cycles to get higher quality data at the expense of having to let the scan run overnight.

5. Improve AI models
In the Neural Network/ folder is the code used for my project in AI for Materials. There are several ways to improve the models, including the number of layers, the nodes in each layer, learning rates, weight decays, schedulers, etc. In addition, I included some transformations of the data, such as rotations and reflections. The model appears to be overfitting the training data if the transformations are not included, so maybe there are ways to increase the complexity of the model. However, this would also result in an increase in training times. Again, there are a lot of ways to improve the models. Applying this model to a brand new set of data, in the ApplyingNetwork.ipynb file, there is still a lot of error. 