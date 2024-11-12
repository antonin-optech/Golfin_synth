import cv2
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


# Load the stereo images
left_image = cv2.imread('shots/frame2_left.png', 0)  # Replace with actual filename
right_image = cv2.imread('shots/frame2_right.png', 0)  # Replace with actual filename

# StereoSGBM Parameters
focal_length = 200.0
window_size = 5
min_disp = 0
num_disp = 16*5 - min_disp
stereo = cv2.StereoSGBM_create(minDisparity=min_disp,
                               numDisparities=num_disp,
                               blockSize=window_size,
                               uniquenessRatio=10,
                               speckleWindowSize=100,
                               speckleRange=32,
                               disp12MaxDiff=1,
                               P1=8*3*window_size**2,
                               P2=32*3*window_size**2)

# Compute disparity map
disparity = stereo.compute(left_image, right_image).astype(np.float32) / 16.0

# Reproject to 3D (adjust Q matrix as per your camera configuration)
Q = np.float32([[1, 0, 0, -left_image.shape[1]/2],
                [0, 1, 0, -left_image.shape[0]/2],
                [0, 0, 0, focal_length],  # Replace with actual focal length
                [0, 0, 1, 0]])
points_3D = cv2.reprojectImageTo3D(disparity, Q)

# Filter points
mask = disparity > disparity.min()
out_points = points_3D[mask]

# Assuming 'out_points' is your array of 3D points from the point cloud
# Extracting X, Y, Z coordinates
X = out_points[:, 0]
Y = out_points[:, 1]
Z = out_points[:, 2]

# Creating a figure and a 3D axis
fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')

# Scatter plot
ax.scatter(X, Y, Z, c=Z, cmap='viridis', marker='.')

# Setting labels
ax.set_xlabel('X axis')
ax.set_ylabel('Y axis')
ax.set_zlabel('Z axis')

# Show plot
plt.show()
