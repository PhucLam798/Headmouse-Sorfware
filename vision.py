import cv2
import mediapipe as mp
from math import hypot

mp_face_mesh = mp.solutions.face_mesh

def init_face_mesh():
    return mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

def midpoint(p1, p2):
    return ((p1[0]+p2[0])//2, (p1[1]+p2[1])//2)

def get_blinking_ratio(frame, eye_points, landmarks, w, h):
    left = (int(landmarks[eye_points[0]].x * w),
            int(landmarks[eye_points[0]].y * h))
    right = (int(landmarks[eye_points[3]].x * w),
             int(landmarks[eye_points[3]].y * h))

    top = midpoint(
        (int(landmarks[eye_points[1]].x * w),
         int(landmarks[eye_points[1]].y * h)),
        (int(landmarks[eye_points[2]].x * w),
         int(landmarks[eye_points[2]].y * h))
    )

    bottom = midpoint(
        (int(landmarks[eye_points[5]].x * w),
         int(landmarks[eye_points[5]].y * h)),
        (int(landmarks[eye_points[4]].x * w),
         int(landmarks[eye_points[4]].y * h))
    )

    cv2.line(frame, left, right, (0,255,0), 2)
    cv2.line(frame, top, bottom, (0,255,0), 2)

    hor = hypot(left[0]-right[0], left[1]-right[1])
    ver = hypot(top[0]-bottom[0], top[1]-bottom[1])

    return hor / ver if ver != 0 else 0