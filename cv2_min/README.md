cv2_min stands for minified cv2. Currently it does just that - exposes Python 3 bindings of select parts of cv2.

Usage: copy cv2_min contents to C.H.I.P., execute `make` in its Debian shell, and place the resulting cv2_min.so file on your PYTHONPATH to be able to import cv2_min in your programs.

This approach was informed by https://www.learnopencv.com/how-to-convert-your-opencv-c-code-into-a-python-module/.
