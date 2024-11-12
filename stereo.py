import cv2
import numpy as np
import matplotlib.pyplot as plt


baseline_distance = 3.0
focal_length = 1.0

# Load the stereo images
left_image = cv2.imread('shots/frame2_left.png', cv2.IMREAD_GRAYSCALE)
right_image = cv2.imread('shots/frame2_right.png', cv2.IMREAD_GRAYSCALE)

# Create a stereo block matching object
stereo = cv2.StereoBM_create(numDisparities=64, blockSize=15)

# Compute the disparity map
disparity = stereo.compute(left_image, right_image).astype(np.float32) / 16.0

depth = np.zeros_like(disparity)
mask = disparity > 0  # Avoid division by zero
depth[mask] = (focal_length * baseline_distance) / disparity[mask]

depth_normalized = cv2.normalize(depth, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)

# Display the disparity map
_, thresh = cv2.threshold(left_image, 10, 255, cv2.THRESH_BINARY)
contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
hull = cv2.convexHull(contours[0])
(x0, y0), (w, h), angle = cv2.fitEllipse(hull)
# Golf balls are typically not less than 42.7 mm in diameter
# Here we have 224.83 pixels = 42.7 mm, scale is 
scale = w/42.7 #5.26 px/mm

# For a distance of z = 75, the camera is 14.26 mm away

c_img = np.zeros((*left_image.shape, 3))
drawn = cv2.drawContours(c_img, contours, -1, (255, 0, 0), -1)

# plt.figure()
# plt.imshow(depth)
# plt.show()

# cv2.imshow('Disparity Map', depth_normalized)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
cv2.imwrite("depth_image.png", depth)

# plt.imshow(depth_normalized, cmap='plasma')
# plt.show()
plt.imsave('depth.png', depth_normalized, cmap='plasma')