import cv2
import cv2.aruco as aruco

dictionary = aruco.getPredefinedDictionary(aruco.DICT_5X5_50)

# OpenCV-version-compatible marker generation
if hasattr(aruco, "generateImageMarker"):
    marker = aruco.generateImageMarker(dictionary, 0, 700)
elif hasattr(aruco, "drawMarker"):
    marker = aruco.drawMarker(dictionary, 0, 700)
else:
    marker = aruco.Dictionary.generateImageMarker(dictionary, 0, 700)

cv2.imwrite("marker0.png", marker)
print("SUCCESS: marker0.png created")

