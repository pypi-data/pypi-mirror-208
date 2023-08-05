import cv2
# import matplotlib.pyplot as plt
# Acquire a sample image and specify its current size:
# read image
img = cv2.imread("my-image.jpg")
print('Image Width is', img.shape[1])
print('Image Height is', img.shape[0])
# Resize the image of, say, a size of 800×600 pixels, to 300×300 pixels:
imgResize = cv2.resize(img, (300, 300))
print('end', img.shape)

img = cv2.imread('my-image.jpg', cv2.IMREAD_GRAYSCALE)
# cv2.imshow('image', img)
cv2.imshow('image', imgResize)
cv2.imwrite('img/img2.jpg', imgResize)

cv2.waitKey(0)
cv2.destroyAllWindows()
