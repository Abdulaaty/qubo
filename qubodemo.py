"""
    /*
    ======================================================
  QUBO-P - 20 Button Version with RGB LED and Auto Simulate Option
 
 
  Omar Abdulaaty - March 2021
  omar.abdulaaty@tu-dortmund.de
  TU Dortmund LS8 
    ======================================================
    */


  Protocool Guide: 
  S ==> Start Matrix transmission (client to arduino)
  A ==> Auto solution mode
  G ==> get Matrix client (arduino to clinet)
  B ==> get Buttons status (arduino to clinet)
  K ==> set buttons status (client to arduino)
  D ==> auto solution mode with delay and iterations
  U ==> blink hint
  
  C ==> Reserved for ack. of cost function values 
  
  
   Functions Guide: 
    format_number           : reformat the number to 2-byte-big-endian number to be read by Arduino
    solve                   : solves the problem automatically using input delay and number of iterations 
    button_status           : returns the desired button(s) status, returns all if nothing is passed
    toggle_button           : toggles the desired button(s), toggles all if nothing is passed
    reset                   : resets the problem
    close                   : closes the serial channel
    hint                    : blinks a hint
    set_button_status       : sets the selected buttons to 1, sets all if nothing is passed
    solve_qubo              : return the best_x , best_value, worst_value for a passed Q (param matrix)
    get_matrix_parameters   : returns the current parameters matrix in Arduino
    load_parameters         : load parameters to the arduino
    buffer_is_not_empty     : checks if the buffer is empty or not
    empty_buffer            : empties the buffer from any information
            
      
"""

import serial
import time
import itertools
import numpy as np


class QUBODemonstrator:  
    def __init__(self, channel_String):
        if (type(channel_String)!=str):
             print ("Enter a Valid String")
             exit(1)
        try:
            self.ser = serial.Serial(channel_String,timeout=1, baudrate=9600)
            # Class variables to be used internally
            self.__Channel_String = channel_String 
            # Default value for problem size
            self.__N = 20 
            # give arduino time to initialize comm. port
            time.sleep(2)  
        except: 
            error_msg = "Connection not possible, check USB or communication port name"
            raise RuntimeError(error_msg) from None
          
            
    def format_number(self,number_to_send):
        # Format number for sending to arduino
        formatted_number = int.to_bytes(number_to_send, length=2, byteorder='big', signed=True)
        return formatted_number   
    
    def solve(self,delay = 100,iterations=50):
        # Empty the buffer
        self.empty_buffer()
        
        # Get inputs as int to avoid doubles
        delay_input = int(delay)
        iter_input = int(iterations)
        # Start solve request
        self.__request('D')
     
        # Print after "Solving with:" from __request('D')
        print ("{} ms delay ... ".format(int(delay_input)))
    
        # Sending delay
        self.ser.write(self.format_number(delay_input))
        self.getMsg()
        
        # Sending interations
        self.ser.write(self.format_number(iter_input))
        self.getMsg()
        
        # Wait until the arduino finishes solving
        time.sleep(10*iter_input*delay_input/1000)     
        msg = self.ser.readline()
        while(not msg):
            print ("Waiting for Response from arduino after solving... ")
            msg = self.ser.readline()
        #print(msg)    
        self.__task_acknowledgement('D',msg)    
        return 
    
    
    def button_status(self, buttons = None):        
        # Assigning default values
        if buttons is None:
            buttons = np.arange(self.__N)
        # All buttons status
        curr_buttons = self.get_buttons_status()
        # get only requested buttons
        requested_buttons =  [ curr_buttons[i] for i in buttons]
        print ([curr_buttons[i] for i in buttons])
        return requested_buttons
    
    def toggle_button(self,buttons = None):
         # Assigning default values
        if buttons is None:
            buttons = np.arange(self.__N)
        # Get current buttons status    
        curr_buttons = self.get_buttons_status()
        # toggle requested buttons
        for curr_index in buttons:
            curr_buttons[curr_index] =  self.toggle(curr_buttons[curr_index])
        # set buttons status    
        self.set_buttons_status(curr_buttons)
        return
    
    def reset(self):
        # Enable connecting to serial port by closing the current port
        self.ser.close() 
        # Exception Checker
        try:
            self.ser = serial.Serial(self.__Channel_String,timeout=1, baudrate=9600)
            print ("Problem restarted, default values are loaded")
            time.sleep(2)  
        except: 
            error_msg = "Connection not possible, problem didn't restart successfully.\nPlease re-run the algorithm"
            raise RuntimeError(error_msg) from None
   
    def close(self):
        self.ser.close()

    def hint(self):
        # Get current parameters, button status and current fitness value
        curr_Matrix = self.get_matrix_parameters()
        curr_buttons = self.get_buttons_status()
        curr_value = np.dot(curr_buttons, np.dot(curr_Matrix, curr_buttons))   
        
        # Loop through all possible combinations
        best_value = -np.infty
        best_index = -1
        for curr_index in range(0,self.__N):   
            
            curr_buttons[curr_index] =  self.toggle(curr_buttons[curr_index])
            new_value = np.dot(curr_buttons, np.dot(curr_Matrix, curr_buttons))
            if (new_value > best_value):
                best_value = new_value
                best_index = curr_index
            curr_buttons[curr_index] =  self.toggle(curr_buttons[curr_index])
        
        # blink the hint, or return error code -1
        if (best_value > curr_value ):    
            self.blink(best_index)
            return best_index
        else: 
            # No maximum is possible
            self.blink(-1)
        return -1
    
    def toggle(self,x):
        return 1-x
    
    
    def blink(self,button_index):
        # Empty the buffer
        self.empty_buffer()
        # send to arduino button to be blinked
        self.__request('U')
        number_to_send =int(button_index)
        self.ser.write(self.format_number(number_to_send))
        return
    
    def get_buttons_status(self):
        # Empty the buffer
        self.empty_buffer()
        
        print ("Getting buttons status... ")
        self.__request('B')
        # initialize return msg
        buttons = np.zeros(self.__N)
        #read all buttons
        for curr_index in range(0,self.__N):
            msg = self.getMsg()             
            buttons[curr_index] = int(msg)
            
        self.__task_acknowledgement('B')    
        return buttons     
    
    def set_buttons_status(self, buttons = None):
        # Empty the buffer
        self.empty_buffer()
        
        # Assigning default values
        if buttons is None:
            buttons = np.ones(self.__N)    
        print ("Setting buttons status... ")    
        # set buttons after the request is successful 
        self.__request('K')    
        
        for curr_index in range(0,self.__N):
             number_to_send =int( buttons[curr_index])
             self.ser.write(self.format_number(number_to_send))
             self.getMsg()
            
        self.__task_acknowledgement('K')    
        return 
    
    def solve_qubo(self,Q):
        print("Solving optimal problem...")
        
        # Solves the problem by brute-force
        n = Q.shape[0]
        best_value = -np.infty
        worst_value = np.infty
        for x in itertools.product([0,1], repeat=n):
            value = np.dot(x, np.dot(Q, x))
            if value > best_value:
                best_x = x
                best_value = value
            if value < worst_value:
                worst_value = value
        print("Solved")        
        return best_x, best_value, worst_value

  
    def get_matrix_parameters(self):
        # Empty the buffer
        self.empty_buffer()
        
        print ("Getting QUBO parameters... ")
        self.__request('G')
        
        n = self.__N    
        tri_indicies = np.triu_indices(n)    
        Q = np.zeros((n,n), dtype=np.float64)    
        for curr_index in range(0, len(tri_indicies[0])):
            msg = self.getMsg()
            Q[tri_indicies[0][curr_index],tri_indicies[1][curr_index]] = int(msg)
            
        self.__task_acknowledgement('G')    
        return Q 

    def __request(self, signal):
        #Signal that will be recieved
        signal_recieve = signal.lower()
        signal_send = bytes(signal, 'utf-8')
        self.ser.write(signal_send)
        msg =self.getMsg()
          
        # get messages to indicate the status of the transmission  
        success_msg, error_msg = self.get_messages(signal)
        
        if (msg.strip().decode("utf-8")  == signal_recieve):
            print(success_msg)
        else:
            print(msg.strip().decode("utf-8"))
            raise RuntimeError(error_msg)

        return
      
    def get_messages(self,signal):
        
        all_success_msgs={
                'S':"Starting Transmission!",
                'D':"Solving with:",
                'U':"A hint is shown on the demonstrator :D",
                'B':"Starting Reception!",
                'K':"Starting Transmission!",
                'G':"Starting Reception!",
                'A':"Solving..."
             }
        
        all_error_msgs ={
                'S':"Failed to begin transmission!",
                'D':"Failed to start solving automatically...\nFailed to begin transmission of input delay",
                'U':"Failed to present the hint",
                'B':"Failed to begin reception",
                'K':"Failed to begin transmission",
                'G':"Failed to begin reception",
                'A':"Failed to start solving automatically..."
             }
            
    
        success_msg = all_success_msgs.get(signal,404)    
        # Check msg validity
        if success_msg == 404:
            raise RuntimeError("Signal not defined in the protocol")
       
        error_msg = all_error_msgs.get(signal,404)   
         # Check msg validity  
        if error_msg == 404:
            raise RuntimeError("Signal not defined in the protocol")
            
        return success_msg, error_msg
    
        
    def __task_acknowledgement(self,signal, msg = None):  
        # No acknoledgment from hint 
        if signal == 'U' :
            return
        # get ack message
        if msg is None:
            msg =self.getMsg() 
            
        # check the task status with predefined message protocol 
        success_msg, error_msg = self.get_ack_messages(signal)
        
        if (msg.strip().decode("utf-8") == '!'):
            print(success_msg)
        else:
            raise RuntimeError(error_msg)
            
            
    def get_ack_messages(self,signal):
        all_success_msgs={
                'S':"Matrix Transmission Done!",
                'C':"Transmission ended successfully",
                'D':"AutoMode done!:",
                'U':"No ack to show",
                'B':"Buttons Reception Done!",
                'K':"Buttons Transmission Done!",
                'G':"Matrix Reception Done!",
                'A':"AutoMode done!"
             }
        
        all_error_msgs ={
                'S':"Failed to transmit the matrix",
                'C':"Failure in Transmission",
                'D':"Failed to solve automatically",
                'U':"No ack to show",
                'B':"Failed to receive the buttons",
                'K':"Failed to set the buttons",
                'G':"Failed to receive the matrix",
                'A':"Failed to solve automatically"
             }
        success_msg = all_success_msgs.get(signal,404)    
        # Check msg validity
        if success_msg == 404:
            raise RuntimeError("Signal not defined in the protocol")
       
        error_msg = all_error_msgs.get(signal,404)   
         # Check msg validity  
        if error_msg == 404:
            raise RuntimeError("Signal not defined in the protocol")
            
        return success_msg, error_msg  
    
    
    def buffer_is_not_empty(self):
        
        '''
        Use this function if inside rated loop as the condition if there
        is any chnage in arduino side'
        '''
        # Check if there are any information in the buffer
        return self.ser.in_waiting > 0
            
        
    
    def empty_buffer(self):
        # Makes the buffer empty if there are anything in it
        while self.buffer_is_not_empty():
            disregarded_msg = self.getMsg()   
            
            #print(disregarded_msg)
        return 
    
    def getMsg(self):
        msg =self.ser.readline()
        while(not msg):
            print ("Waiting for Response... ")
            time.sleep(0.01)
            msg =self.ser.readline()  
        return msg    
    
    def load_parameters(self,params,best_x = None , best_value= None, worst_value= None):
        # Empty the buffer
        self.empty_buffer()
        
        # Get problem size 
        n = int(np.sqrt(2*params.shape[0]))
        self.__N = n
        # Initialize matrix for qubo problem
        Q = np.zeros((n,n), dtype=np.float64) 
        tri_indicies = np.triu_indices(n)
        params_iterator= 0
        for curr_index in range(0, len(tri_indicies[0])):
            Q[tri_indicies[0][curr_index],tri_indicies[1][curr_index]] = int(params[params_iterator])
            Q[tri_indicies[0][curr_index],tri_indicies[1][curr_index]] = (params[params_iterator])
            params_iterator+=1
        
        # Solve the qubo problem
        if best_x is None or best_value is None or worst_value is None:
            best_x , best_value, worst_value = self.solve_qubo(Q)
            
        ValuesRange = best_value-worst_value
        print(best_x)
        print(best_value)
        print(worst_value)
        
        self.__request('S')
       
        #Sending the parameters    
        errorCount = 0
        for curr_index in range(0, len(tri_indicies[0])):
            number_to_send =int( Q[tri_indicies[0][curr_index],tri_indicies[1][curr_index]])
            self.ser.write(self.format_number(number_to_send))
           
            msg =self.getMsg()
            if (int(msg) !=  number_to_send):
                print ("Error while sending weight matrix")
                print(number_to_send)
                print(self.format_number(number_to_send))
                print(int(msg))
                print(self.format_number(int(msg)))
                errorCount+=1
            
        if(errorCount ==0):
            print  ("All parameters are sent and received successfully")
        else:
           print  ("Failed to send",errorCount," Parameters")
       
        
        self.__task_acknowledgement('S')
        
        # Sending optimal combination
        errorCount = 0
        for curr_index_2 in range(0, len(best_x) ):
            number_to_send = int(best_x[curr_index_2])  
            self.ser.write(self.format_number(number_to_send))
            msg =self.ser.readline()
            while(not msg):
              print ("Waiting for Response... ")
              msg =self.ser.readline()
            if (int(msg) !=  number_to_send):
                print ("Error while sending optimal combination ")
                errorCount+=1
        if(errorCount ==0):
            print  ("Optimal values are sent and received successfully")
        
        # Sending Min and range
        errorCount =0   
        number_to_send = int(worst_value) 
        self.ser.write(self.format_number(number_to_send))
        msg =self.ser.readline()
        while(not msg):
            print ("Waiting for Response... ")
            msg =self.ser.readline()
        if (int(msg) !=  number_to_send):
            print ("Error while sending min value ")
            errorCount+=1    
        
        number_to_send = int(ValuesRange) 
        self.ser.write(self.format_number(number_to_send))
        msg =self.ser.readline()
        while(not msg):
            print ("Waiting for Response... ")
            msg =self.ser.readline()
        if (int(msg) !=  number_to_send):
            print ("Error while sending range of values")
            errorCount+=1      
        if(errorCount ==0):
           print  ("Min value and range of values are sent successfully")  
           
        self.__task_acknowledgement('C')
        
        return

def check_input(user_input, range_of_inputs):
    valid_input = True
    try:
       # check if the input is valid (not a number, not in options ...)
       if float(user_input) not in range_of_inputs :
           raise ValueError
          
    except:
        print("not a valid input, please enter a correct input...")
        valid_input= False
        time.sleep(2)     
    return valid_input

def check_param_file(user_input):
      valid_input = True
      try:
       # check if the input is valid (load the file)
        np.load(user_input)         
        
      except:
            print("not a valid input, please enter a correct file name...")
            valid_input= False
            time.sleep(2)     
      return valid_input


def print_optimal_combination(Q,best_x=0 , best_value=0, worst_value=0): 
    table = str.maketrans('[]','{}')
    print(np.array2string(Q, separator=', ').translate(table))
   # if intentionally best_value is smaller, skip printing
    if best_value > worst_value:
        print("Best combination is:")
        print(best_x)
        print("With best value:")
        print(best_value)
        print("With worst value:")
        print(worst_value)    
    return
         
def main():
    channle_str = input("Enter port name:")
  

    dev = QUBODemonstrator(channle_str)
    
    range_of_inputs = range(1,10)
    user_output_msg = "\n Choose one of the options \n (1) to upload new weight matrix \n (2) to solve the problem automatically \n (3) to solve the problem automatically with delay \n (4) to get the matrix parameters \n (5) to get the current button status \n (6) to set the buttons status \n (7) to get a hint  \n (8) to reset the problem \n (9) to exit \n"
   
    """
    Options: 
    (1) to upload new weight matrix
    (2) to solve the problem automatically
    (3) to solve the problem automatically with delay
    (4) to get the matrix parameters
    (5) to get the current button status
    (6) to set the buttons status 
    (7) to get a hint
    (8) to reset the problem 
    (9) to exit
   
    """
    while True: 
        
        # Get input operation and check validity
        valid_input = False
        while not valid_input:
            user_input = input(user_output_msg)
            valid_input = check_input(user_input, range_of_inputs)   
                 
        if(int(user_input) == 9):
            exit(0)
                 
        if(int(user_input) == 8):
            dev.reset()
            
        if(int(user_input) == 7):
            dev.hint()
          
        if(int(user_input) == 6):
            dev.set_buttons_status()

        if(int(user_input) == 5):
            buttons = dev.get_buttons_status()
            print(buttons)
        
        if(int(user_input) == 4):
            Q= dev.get_matrix_parameters()    
            print_optimal_combination(Q) 
        

        if(int(user_input) == 3):
            range_of_delay = range(1,10000)
            # Check that input delay is correct
            valid_input2 = False
            while not valid_input2:
                delay_input = input("Please enter the delay in ms (1 to 10000) ")
                valid_input2 = check_input(delay_input, range_of_delay)            
            
            
            range_of_iter = range(1,100)
            # Check that input iterations is correct
            valid_input3 = False 
            while not valid_input3:
                iter_input = input("Please enter the number of iterations (1 to 100)")
                valid_input3 = check_input(iter_input, range_of_iter)            
            
            #Solve auto mode with the given input delay
            dev.solve(delay=delay_input, iterations=iter_input)
             
        if(int(user_input) == 2):
            dev.solve()
            
        if(int(user_input) == 1):
            # Get file name and check validity
            valid_file = False 
            while not valid_file:
                file_input = input("Please enter file name: ")
                valid_file = check_param_file(file_input)  
            # Load file to arduino    
            params = np.load(file_input)      
            print(params)
            dev.load_parameters(params)
           
           
           
if __name__ == '__main__':
    main()           