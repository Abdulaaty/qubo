"""
    /*
    ======================================================
  QUBO-P - Visualizer
 
 
  Omar Abdulaaty - March 2021
  omar.abdulaaty@tu-dortmund.de
  TU Dortmund LS8 
    ======================================================
    */
               
"""


# Import pygame and needed modules

import pygame
import math
import time
import random
import numpy as np
import cluster_binary
from qubodemo import QUBODemonstrator




# define limits of pygame window
size_x = 1080
size_y = 720

ml2r_x = 5
ml2r_y = 5
ml2r_x_size = 200
ml2r_y_size = 75


  
def isInside(click_pos, circle_center): 
    # check if click is inside the circle defined by the circle center
    global circle_radius
    dx = (click_pos[0] - circle_center[0] - circle_radius)**2
    dy = (click_pos[1] - circle_center[1] - circle_radius)**2
    
    return  math.sqrt(dx+dy) <= circle_radius






def sample_new_cluster(dev):
    global circle_radius
    # get the cluster points and paramteresmatrix
    Q,points1,points2 = cluster_binary.get_qubo_params_random()
    # Transfer the problem to maximization
    Q = -Q 
    # Only int 
    Q = Q.astype(int)
    
    
    # Get drawing postions
    positions =   np.vstack(  (points1,points2) )    
    # transform postions to positve onl
    min_value = np.amin(positions) 
    positions = positions + np.abs(min_value)
    # scale postions to 0~1
    max_value = np.amax(positions)   
    positions = positions/max_value
    # scale postions to screen
    positions = positions * [[size_x - 2*circle_radius-4,size_y -ml2r_y_size-2*circle_radius ]]
    # add a shift for logo
    positions = positions + [[2,ml2r_y_size]]
    # transform it to int to index pixles
    positions = positions.astype(int)
    
    
    
    '''
    Since the problem is approximated using integers, then the 2 maximums are not exactly equal, 
    so we need to find the best max and worst min to send it to arduino
    '''
    # Pre-assign max and min values
    best_x1 = [1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0] 
    best_x2 = [0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1]
    
    value1 = np.dot(best_x1, np.dot(Q, best_x1))
    value2 = np.dot(best_x2, np.dot(Q, best_x2))
    if value1>value2:
        best_x = best_x1
        best_value = value1
    else:
        best_x = best_x2
        best_value = value2
        
    worst_x1 = np.zeros(20)
    worst_x2 = np.ones(20)
    value1 = np.dot(worst_x1, np.dot(Q, worst_x1))
    value2 = np.dot(worst_x2, np.dot(Q, worst_x2))
    
    if value1>value2:
        worst_value = value2
    else:
        worst_value = value1
        
    # Arduino takes the 210 elements from the triangular 20x20 matrix
    # get 210 vector from 20x20 matrix
    Q = cluster_binary.get_parameters_from_matrix(Q)
    try:
        dev.load_parameters(Q,best_x = best_x , best_value= best_value, worst_value=worst_value )
    except:
        print(len(Q))
        print(Q)
        print(Q.shape)
        
    curr_Matrix = dev.get_matrix_parameters()

    return positions, best_value, worst_value, curr_Matrix    

  

     
def main():
    global circle_radius
    # define constant values
    circle_radius = 15
    rate = 0.1 
    
    
    
    
    
    # Get channel (port) name from user
    channle_str = input("Enter port name:")
    
    # instantiate a qubo class and get the current params and status
    dev = QUBODemonstrator(channle_str)
   
    
    # sample new points with solution best_x1 and best_x2
    positions, best_value, worst_value, curr_Matrix  = sample_new_cluster(dev)  
    # get random initial configuration
    random_buttons = [random.randint(0, 1) for _ in range(20)]
    button_states = np.array(random_buttons)
    dev.set_buttons_status(button_states)    
  
  
    
 
    # Initialise pygame and setting the screen
    pygame.init()
    pygame.display.set_caption('QUBO Game')          
    screen = pygame.display.set_mode((size_x, size_y))
    pygame.display.update()  
    
    # load the logo and on-off circle images
    ml2r_logo = pygame.image.load("ml2r.jpg")
    ml2r_logo_resized = pygame.transform.smoothscale(ml2r_logo, (ml2r_x_size, ml2r_y_size))
    circle_on = pygame.image.load("circle_on.png")
    circle_off = pygame.image.load("circle_off_dark.png")
   
    # fill screen with white then load the logo the the game screen
    screen.fill([255,255,255])
    screen.blit(ml2r_logo_resized, (ml2r_x, ml2r_y))

    # Flag for the loop     
    running = True
    
    #rate start time
    start_time =  time.time()
    
    while running : 
        # get time for rate calculation
        current_time = time.time()
        elapsed_time = current_time - start_time
        
        # Update display
        pygame.display.update()
        
        # check rate, if rate is passed, check button status
        if (elapsed_time > rate):
            if dev.buffer_is_not_empty():
                # a button has changed
                changed_index = int(dev.ser.readline())
                # Toggle changed index
                button_states[changed_index] = 1 - button_states[changed_index] 
                # Update game status values 
             
            #recompute for next iteration     
            start_time =  time.time()    
        
    
        # Draw circles in the points location
        for i, circle_pos in enumerate(positions):    
                if button_states[i]: 
                    screen.blit(circle_on, (circle_pos[0],circle_pos[1]))
                else:
                    screen.blit(circle_off, (circle_pos[0],circle_pos[1]))
        
                
        '''
        The remaining part is to handle changing the demo from the game as well as
        closing the game
        '''
        # flag to indicate buttons are changed from the game     
        new_button_set = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONUP:
                # get mouse click position
                pos = pygame.mouse.get_pos()
                # check buttons    
                for index, circle_pos in enumerate(positions): 
                        if isInside(click_pos=pos, circle_center=circle_pos): 
                            new_button_set = True
                            if button_states[index]:                   
                                button_states[index] = 0  
                            else:
                                button_states[index] = 1
                            break
                    # send changed buttons to arduino
                if new_button_set:    
                    dev.set_buttons_status(button_states)    
                  
                
       


if __name__ == '__main__':
    main()  
    exit(0)
