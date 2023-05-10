import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
import numpy as np

import sys
sys.path.append('..')

from DataAcquisition import data

cube_pos = [0, 0, 0]
cube_size = 1

def update_cube(i):
    # Get the acceleration data for this time step
    ax = data.get_current_value("imu_acceleration_x")
    if (ax is None):
        ax = 0
    ay = data.get_current_value("imu_acceleration_y")
    if (ay is None):
        ay = 0
    az = data.get_current_value("imu_acceleration_z") 
    if (az is None):
        az = 0
    
    # Update the cube position based on the acceleration data
    cube_pos[0] += ax
    cube_pos[1] += ay
    cube_pos[2] += az
    
    # Define the 8 vertices of the cube
    vertices = np.array([
        [cube_pos[0] - cube_size, cube_pos[1] - cube_size, cube_pos[2] - cube_size],
        [cube_pos[0] + cube_size, cube_pos[1] - cube_size, cube_pos[2] - cube_size],
        [cube_pos[0] + cube_size, cube_pos[1] + cube_size, cube_pos[2] - cube_size],
        [cube_pos[0] - cube_size, cube_pos[1] + cube_size, cube_pos[2] - cube_size],
        [cube_pos[0] - cube_size, cube_pos[1] - cube_size, cube_pos[2] + cube_size],
        [cube_pos[0] + cube_size, cube_pos[1] - cube_size, cube_pos[2] + cube_size],
        [cube_pos[0] + cube_size, cube_pos[1] + cube_size, cube_pos[2] + cube_size],
        [cube_pos[0] - cube_size, cube_pos[1] + cube_size, cube_pos[2] + cube_size]
    ])
    
    # Define the 12 edges of the cube
    edges = np.array([
        [0, 1], [1, 2], [2, 3], [3, 0],
        [4, 5], [5, 6], [6, 7], [7, 4],
        [0, 4], [1, 5], [2, 6], [3, 7]
    ])
    
    # Plot the cube
    ax = fig.add_subplot(111, projection='3d')
    ax.clear()
    ax.set_xlim([-10, 10])
    ax.set_ylim([-10, 10])
    ax.set_zlim([-10, 10])
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('IMU Cube Demo')
    ax.plot(vertices[:,0], vertices[:,1], vertices[:,2], 'bo')
    for e in edges:
        ax.plot(vertices[e,0], vertices[e,1], vertices[e,2], 'b-')
    
    # Return the plot
    return ax

# Define the animation function
def animate(i):
    update_cube(i)

# Create the figure and start the animation
fig = plt.figure()
ani = FuncAnimation(fig, animate, interval=50)
plt.show()