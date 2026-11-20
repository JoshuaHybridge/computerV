import os
import cv2

print("OpenCV:", cv2.__version__)

cascade_dir = cv2.data.haarcascades

print("Directorio Haar Cascade:", cascade_dir)

face_xml = os.path.join(
    cascade_dir,
    "haarcascade_frontalface_default.xml"
)

eye_xml = os.path.join(
    cascade_dir,
    "haarcascade_eye.xml"
)

print("Existe frontalface:", os.path.exists(face_xml))
print("Existe eye:", os.path.exists(eye_xml))

classifier = cv2.CascadeClassifier(face_xml)

print("Clasificador vacío:", classifier.empty())