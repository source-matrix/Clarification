import inspect
import sys
import torchvision.transforms.functional as functional
sys.modules.setdefault('torchvision.transforms.functional_tensor', functional)
from gfpgan.utils.face_restoration_helper import FaceRestoreHelper

print(inspect.signature(FaceRestoreHelper.get_face_landmarks_5))
print(inspect.getsource(FaceRestoreHelper.get_face_landmarks_5))
print(inspect.signature(FaceRestoreHelper.get_face_landmarks_68))
print(inspect.getsource(FaceRestoreHelper.get_face_landmarks_68))
