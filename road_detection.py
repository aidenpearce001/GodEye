import cv2
import numpy as np

# Load the image and convert it to grayscale
img = cv2.imread('map.png')

# Convert to HSV color space
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# Define color ranges for the road markings
orange_lower = np.array([10, 100, 100])
orange_upper = np.array([25, 255, 255])
yellow_lower = np.array([20, 100, 100])
yellow_upper = np.array([35, 255, 255])
white_lower = np.array([0, 0, 200])
white_upper = np.array([255, 30, 255])

# Create masks based on color thresholding
orange_mask = cv2.inRange(hsv, orange_lower, orange_upper)
yellow_mask = cv2.inRange(hsv, yellow_lower, yellow_upper)
white_mask = cv2.inRange(hsv, white_lower, white_upper)

# Combine the masks
mask = cv2.bitwise_or(orange_mask, yellow_mask)
mask = cv2.bitwise_or(mask, white_mask)

# Apply morphological operations to remove noise and fill gaps
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

# Get only the road pixels from the original image
result = cv2.bitwise_and(img, img, mask=mask)

# Display the result
cv2.imshow('Result', result)
cv2.waitKey(0)
cv2.destroyAllWindows()