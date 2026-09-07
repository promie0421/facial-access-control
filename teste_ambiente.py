import cv2
import numpy
import onnxruntime
import insightface
from argon2 import PasswordHasher

print("OpenCV:", cv2.__version__)
print("NumPy:", numpy.__version__)
print("ONNX Runtime:", onnxruntime.__version__)
print("InsightFace:", insightface.__version__)

ph = PasswordHasher()
hash_teste = ph.hash("123456")

print("Argon2 funcionando:", ph.verify(hash_teste, "123456"))