# **Headmouse Software**

---

## **Abstract**

This project proposes a computer vision-based headmouse system to assist individuals with limited hand mobility. The system uses a webcam and MediaPipe Face Mesh to detect and track facial landmarks in real time.

Head movement is captured through the nose position and converted into cursor motion. A smoothing technique based on a sliding window (deque) is applied to reduce noise and improve stability.

Eye blinking is detected using the ratio between horizontal and vertical eye distances. When the eye remains closed for a specific duration, mouse click actions are triggered. The system supports both left and right clicks through independent eye detection.

---

## **Contributors**

**Lam Phuc**
