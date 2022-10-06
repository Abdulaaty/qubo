# QUBO 
Python module for interacting with a demonstrator equipped with 20 buttons connected to Arduino in order to show Quadratic Unconstrained Binary Optimization (QUBO) problem 


## Installation
1- clone this repository  
2- Install needed libraries: `pip install serial pygame numpy`   



## Usage 
### Control Mode 
1- Connect Arduino to the PC   
2- Run `qubodemo.py`  
3- You can control the arduino from the terminal by sending the availble commands from terminal  
  
  
![alt text](https://github.com/Abdulaaty/qubo/blob/main/images/cmd_screenshot.png?raw=true)

### Visualizer Mode (Interactive game mode)
1- Connect Arduino to the PC   
2- Run `visualizer.py`   
3- You can control the visualizer by the demonstrator or the visualizer itslef by clicking on the points  

<img src="https://github.com/Abdulaaty/qubo/blob/main/images/visualizer_screenshot.png" width="500" height="334">

## Example
The `qubodemo.py` can be used independently (e.g. for any new visualizer) 
### How to control the demo
```python 
import numpy as np
from qubodemo import QUBODemonstrator

dev = QUBODemonstrator('COM4')  # COM4 is the my port for Adruino, change it to your port
params = np.random.randint(-2**15, 2**15-1, size=210)
dev.load_parameters(params)
dev.button_status(buttons=[0, 4, 19]) # return status of buttons 0, 4 and 19
>>> [0, 1, 1]
dev.button_status() # return status of all buttons
>>> [1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1]
dev.toggle_button([3, 4]) # virtually press buttons 3 and 4
dev.hint() # return button that yields best improvement (or -1) 
>>> 9
dev.set_buttons_status(buttons = [6,9,10]) # sets buttons 6 ,9 ,10 to 1
Q = dev.get_matrix_parameters() # returns Parameter Matrix in Arduino
dev.solve(delay=500)
dev.reset()
dev.close()
```


### Rated loop for visualizer
```python 
import time
vis_running = True
rate = 0.1
start_time =  time.time()

while vis_running:
     current_time = time.time()
     if current_time - start_time > rate:
        # update start time
        start_time =  time.time()
        # check demo in rated loop
        if dev.buffer_is_not_empty():
           pressed_button = dev.ser.readline()
           # do something in your visualizer
     if Terminating_condition_reached: 
        vis_running = False
     

dev.close()

```




