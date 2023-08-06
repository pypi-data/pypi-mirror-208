import cv2

# Load the image
image = cv2.imread("static/img/chan-dung.jpg")

# Convert the image to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Apply a threshold to the grayscale image
ret, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

# Find the contours of the objects in the thresholded image
contours, hierarchy = cv2.findContours(
    thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# Find the largest contour in the image
largest_contour = max(contours, key=cv2.contourArea)

# Extract the bounding box of the largest contour
(x, y, w, h) = cv2.boundingRect(largest_contour)

# Crop the image to remove the background
cropped_image = image[y:y+h, x:x+w]

# Save the cropped image
cv2.imwrite("static/img/sketch/cropped_image.jpg", cropped_image)
