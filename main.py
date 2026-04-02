import cv2
import pyautogui

import config as cfg
from vision import init_face_mesh, get_blinking_ratio
from control import HeadMouse

def main():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, cfg.FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cfg.FRAME_HEIGHT)

    face_mesh = init_face_mesh()
    headmouse = HeadMouse(cfg)

    font = cv2.FONT_HERSHEY_SIMPLEX

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Không đọc được camera")
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = face_mesh.process(rgb)

        mouse_x, mouse_y = pyautogui.position()

        if not results.multi_face_landmarks:
            cv2.putText(frame, "KHONG PHAT HIEN MAT",
                        (10, 30), font, 1, (0,0,255), 2)
        else:
            landmarks = results.multi_face_landmarks[0].landmark

            # vẽ landmark
            for lm in landmarks:
                x = int(lm.x * cfg.FRAME_WIDTH)
                y = int(lm.y * cfg.FRAME_HEIGHT)
                cv2.circle(frame, (x,y), 1, (0,255,0), -1)

            # 👉 mũi
            x = landmarks[1].x * cfg.FRAME_WIDTH
            y = landmarks[1].y * cfg.FRAME_HEIGHT

            mouse_x, mouse_y = headmouse.move(x, y)

            # blink
            left_ratio = get_blinking_ratio(frame, cfg.LEFT_EYE, landmarks,
                                            cfg.FRAME_WIDTH, cfg.FRAME_HEIGHT)

            right_ratio = get_blinking_ratio(frame, cfg.RIGHT_EYE, landmarks,
                                             cfg.FRAME_WIDTH, cfg.FRAME_HEIGHT)

            click = headmouse.handle_click(left_ratio, right_ratio)

            if click == "LEFT":
                cv2.putText(frame, "Click Trai!", (10,90), font, 0.7, (0,255,0), 2)

            elif click == "RIGHT":
                cv2.putText(frame, "Click Phai!", (10,150), font, 0.7, (0,255,0), 2)

            cv2.putText(frame, f"TY LE TRAI: {left_ratio:.2f}",
                        (10,120), font, 0.7, (255,0,0), 2)

            cv2.putText(frame, f"TY LE PHAI: {right_ratio:.2f}",
                        (10,180), font, 0.7, (255,0,0), 2)

        # hiển thị tọa độ
        cv2.putText(frame, f"TOA DO: ({int(mouse_x)}, {int(mouse_y)})",
                    (10,60), font, 0.7, (255,0,0), 2)

        cv2.imshow("HeadMouse", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()