from pathlib import Path
import cv2

path = Path('docs/assets/before-after/before.jpeg')
image = cv2.imread(str(path), cv2.IMREAD_COLOR)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
face = cv2.CascadeClassifier(str(Path(cv2.data.haarcascades) / 'haarcascade_frontalface_default.xml'))
eye = cv2.CascadeClassifier(str(Path(cv2.data.haarcascades) / 'haarcascade_eye_tree_eyeglasses.xml'))
faces = face.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=5, minSize=(80,80))
print('image', image.shape, 'faces', faces.tolist())
for x, y, w, h in faces:
    roi = gray[y:y + int(h * 0.62), x:x+w]
    eyes = eye.detectMultiScale(roi, scaleFactor=1.05, minNeighbors=5, minSize=(20,20))
    print('face', (x,y,w,h), 'eyes', eyes.tolist())
