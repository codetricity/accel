import sys, pygame
from pygame.locals import *
from math import ceil
from math import cos, sin
from random import randint
# For linear algebra
import numpy as np
import pygame 

from copy import deepcopy # cheap hack; shot myself in the foot with python references in the list

# set up global variable SCREEN
SCREEN = pygame.Surface((480, 320))

# Model the Boid as an object, as Reynolds suggests in the paper 
# (OOP was not as popular back in 1987; this was originally done in Common LISP)

###############################################################################################################
# Model of the Boid
#   * Could be considered an animal, such as a fish or bird, or a robot
#   * Can only "see" within a small distance (a couple of body lengths), which I call the parameter "neighbor_distance"
#   * The naive complexity is in O(n^2), but it only takes each actor constant time
#       * A massive implementation could use a spatially sorted datastructure such as kD-tree (quad-tree in two dimensions, 
#         octree in three dimensions) for fast approximate nearest neighbors
#   * Resulting behavior is often referred to in the literature as "Emergent Behavior"
#   * If you think the type of dynamical system is interesting, check out cellular automata [5]
#
# Rules
#   * Rule 1: Tries to stay at least "safe_distance" away from its neighbors
#   * Rule 2: Tries to fly toward the center of mass of all neighbors within "neighbor_distance"
#   * Rule 3: Tries to match velocity with the neighbors within neighbor_distance
#
# Coordinate System
#   * The coordinate system in pygame has (0,0) in the top left corner, with "+x" horizontal to the right, and "+y" vertically pointing downward.
###############################################################################################################

def saturate(value, max_value):
    if abs(value) > max_value:
        return np.sign(value)*max_value
    return value

class Boid:
    #: Initialize the boid at some position x,y
    def __init__(self, x, y, angle, image_surface):
        #######################################################################################################
        # Dynamical State
        #######################################################################################################
        #: position
        self.pos = np.array([x, y]) # [px] right = +x, down = +y, (0,0) in top left corner
        self.angle = angle # [deg] up = +x = 0[deg], left = +y = 90[deg]; current heading
                
        #: velocity
        # [x, y]
        self.vel = np.array([0.,0.])
        self.rot_vel = 0.0
        
        #: acceleration (this is what the rules affect)
        # [translational, rotational]
        self.accel = np.array([0.0, 0.0])
        self.a2 = np.array([0.,0.])
        
        #######################################################################################################
        # Rendering
        #######################################################################################################
        #: image & rendering surfaces
        self.image_surface = image_surface
        self.surf = pygame.Surface((51,51),flags=pygame.SRCALPHA)
        self.surf.set_alpha(0)
        tmp_rect = self.image_surface.get_rect()
        self.pos_rect = pygame.Rect((16,16,17,17))
        self.surf.blit(image_surface, self.pos_rect)
        
        ############################################
        #: Boid Parameters
        ############################################
        self.max_vel = np.array([25., 20.])
        self.max_accel = np.array([12., 5.]) # magnitude [px] / frame; rotational [deg] / frame
        self.repulsion_coef = 0.5
        self.max_rot_vel = 5
    def __repr__(self):
        return "%.0f,%.0f:%.0f,%.0f " % (self.pos[0], self.pos[1], self.vel[0], self.vel[1]) 
    
    def draw(self):
        #: Rotate the image to the desired heading
        render_angle = -(self.angle+90)
        render_surf = pygame.transform.rotozoom(self.surf, render_angle, 1.0)
        #: Crop the Surface box
        rot_rect = render_surf.get_rect(center=(self.pos[0], self.pos[1]))
        #: Overlay heading 
        #font = pygame.font.Font(None, 12)
        #text = font.render(str(self), 1, (255, 255, 255))
        #r = text.get_rect()
        #render_surf.blit(text, r)
        SCREEN.blit(render_surf, rot_rect)
    
    def update(self, neighbors, close_neighbors, goal, predators=[]):
        #: apply all rules
        self.accel = np.array([0., 0.])

        if len(predators):
            a0 = self.__avoid(predators)
        else:
            a0 = np.array([0.,0.])
        a1 = self.__avoid(close_neighbors)
        a2 = self.__seekgoal(goal)
        a3 = self.__centering(neighbors)
        a4, rot_vel = self.__velocity(neighbors)

        self.accel = 100*a0 

        if np.linalg.norm(self.accel) < self.max_accel[0]:
           new_accel = self.accel + 10*a1
           if np.linalg.norm(self.accel) < self.max_accel[0]:
               self.accel = new_accel
         #+ 0.01*a2 + 0.01*a3 + 0.1*a4

        # Arbitrate acceleration by saturating the acceleration accumulator
        # as in [1]
        if np.linalg.norm(self.accel) < self.max_accel[0]:
           new_accel = self.accel + 0.02*a2
           if np.linalg.norm(self.accel) < self.max_accel[0]:
               self.accel = new_accel
        if np.linalg.norm(self.accel) < self.max_accel[0]:
            new_accel = self.accel + 0.02*a3
            if np.linalg.norm(new_accel) < self.max_accel[0]:
                self.accel = new_accel
        if np.linalg.norm(self.accel) < self.max_accel[0]:
            new_accel = self.accel + 0.02*a4
            if np.linalg.norm(new_accel) < self.max_accel[0]:
                self.accel = new_accel
        
        self.vel = self.accel# + 0.1*self.vel

        # Saturate the Velocity as well
        if np.linalg.norm(self.vel) > self.max_vel[0]:
            self.vel /= np.linalg.norm(self.vel)
            self.vel *= self.max_vel[0]
        
        if np.linalg.norm(self.vel) != 0:
            dir_mvt = np.rad2deg(np.arctan2(self.vel[1],self.vel[0]))
            self.angle = dir_mvt
            self.angle %= 360
       
        self.pos += self.vel

        self.pos[0] %= 1024 # wrap to screen (boids appear on the other side of screen)
        self.pos[1] %= 768 # wrap to screen
    
    ##################################
    # Rules in Order of Precedence
    ##################################

    #: Rule 0: Avoid Predators    
    #: Rule 1: Collision Avoidance
    def __avoid(self, close_neighbors):
        xdot = np.array([0.,0.])
        for i in close_neighbors:
            if i[1] == 0:
                xdot -= i[0].vel
            else:
                xdot -= (i[0].pos-self.pos)/i[1]*(1.0/(i[1])) #*(1.0/i[1]**2) # repulsion is inverse exponentially repulsed by the object
        return xdot

    #: Rule 2: Velocity Matching
    def __velocity(self, neighbors):
        if len(neighbors) == 0:
            return self.vel, self.rot_vel

        sum_vel = np.array([0.,0.])
        sum_rot_vel = 0.

        for i in neighbors:
            sum_vel += i[0].vel
            sum_rot_vel += i[0].rot_vel

        sum_vel /= len(neighbors)
        sum_rot_vel /= len(neighbors)
        
        return sum_vel, sum_rot_vel

    #: Rule 3: Flock Centering
    def __centering(self, neighbors):
        center = np.array([0.,0.])
        
        if len(neighbors) == 0:
            return center
            
        for i in neighbors:
            center += i[0].pos
        
        center /= len(neighbors)
        # compute the direction to the center from current position
        accel_request = (center - self.pos) # vector in pixels
        
        return accel_request

    #: Rule 4: Migratory Urge
    def __seekgoal(self, goal):
        # goal should be np.array([mouse_x, mouse_y])
        accel_request = (goal-self.pos)
        
        #if np.linalg.norm(accel_request) < 500:
        #if np.linalg.norm(accel_request) != 0:
        #    accel_request /= np.linalg.norm(accel_request)
        #else:
        #    accel_request = np.array([0.,0.],dtype=np.float64)
        return accel_request
    
class Flock:
    #: Initializes a flock of @param count boids. Note that birds of a feather
    #: flock together, but that a property of boids is that they can split up
    #: Pseudocode from [3] is adapted here
    def __init__(self, count, safe_distance, neighbor_distance):
        self.image_surface = pygame.image.load("img/fish.png").convert_alpha()
        self.safe_distance = safe_distance # [pixels]; 3 * 20 [px] = 3 body lengths
        self.neighbor_distance = neighbor_distance
        self.boid_list = [ Boid(randint(1,1023), randint(1,768), randint(0,360), self.image_surface) for i in range(count) ]
        self.goal = np.array([0.0, 0.0], dtype=np.float64)
        self.mouse_pos = (0,0) #don't use for computation, just rendering
        self.mouse_predator = False

    #: Render the flock
    def draw(self):
        SCREEN.fill((0,0,0))
        for i in self.boid_list:
            i.draw()
        # draw the goal as a green circle
        pygame.draw.circle(SCREEN, (0,255,0), self.goal.astype(int), 10) # NOTE THAT SCREEN IS A GLOBAL VARIABLE
        # optionally draw the predator as a red circle
        if self.mouse_predator is True:
            pygame.draw.circle(SCREEN, (255,0,0), self.mouse_pos, 10)
        return SCREEN
        
    def update(self, mouse_pos, mouse_predator):
        static_boid_list = self.boid_list[:] # need to research how to avoid this nonsense
        self.mouse_predator = mouse_predator
        self.mouse_pos = mouse_pos
        for i in self.boid_list:
            # find all neighbors within a radius=safe_distance
            close_neighbors = []
            neighbors = []
            predators = []
            
            if self.mouse_predator:
                predator = Boid(mouse_pos[0], mouse_pos[1], 0,  self.image_surface)
                vector_diff = i.pos - predator.pos
                distance = np.linalg.norm(vector_diff)
                if distance < self.safe_distance:
                    predators.append( (predator, distance) )
            else:
                self.goal[0] = mouse_pos[0]
                self.goal[1] = mouse_pos[1]
            for j in static_boid_list:
                vector_diff = i.pos-j.pos
                distance = np.linalg.norm(vector_diff)
                if j == i:
                    continue
                if distance < self.safe_distance:
                    close_neighbors.append( (j, distance) )
                if distance < self.neighbor_distance:
                    neighbors.append( (j,distance) )

            i.update(neighbors, close_neighbors, self.goal, predators)



# #: Setup the pygame Game Engine [2]
# pygame.init()
# fpsClock = pygame.time.Clock()

# #: Configure the screen size (not resizable)
# width = 1024
# height = 768
# size = (width, height)

# black = 1.0, 1.0, 1.0
# white = 255,255,255
# screen = pygame.display.set_mode(size)
# pygame.display.set_caption("Interactive Boid's Algorithm Simulation")

# #: Create and render the initial flock
# f = Flock(30, 100., 500.) # [number of boids], [avoidance_distance], [neighborhood_distance]
# f.draw()
# pygame.display.flip()

# g_mouse_predator = False

# #: Start the simulation
# while True:
# #    fpsClock.tick(30)
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             sys.exit()
#         if event.type == pygame.KEYDOWN:
#             if event.key == K_ESCAPE:
#                 pygame.event.post(pygame.event.Event(QUIT))
#         if event.type == pygame.MOUSEBUTTONDOWN:
#             g_mouse_predator = not g_mouse_predator
#     if True:
#                 screen.fill(white)
#                 f.update(pygame.mouse.get_pos(), g_mouse_predator)
#                 f.draw()
#                 pygame.display.flip()
