import cv2
import dlib
import pyautogui
import os
from pathlib import Path
import time
from math import hypot

# Kiểm tra tệp shape predictor
duong_dan_predictor = "shape_predictor_68_face_landmarks.dat"

# Khởi tạo webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Không thể mở webcam")

# Khởi tạo detector và predictor của dlib
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(duong_dan_predictor)

# Kích thước màn hình và khung hình
chieu_rong_man_hinh, chieu_cao_man_hinh = pyautogui.size()
chieu_rong_khung_hinh, chieu_cao_khung_hinh = 640, 480
cap.set(cv2.CAP_PROP_FRAME_WIDTH, chieu_rong_khung_hinh)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, chieu_cao_khung_hinh)

# Font chữ để hiển thị văn bản trên khung hình
font = cv2.FONT_HERSHEY_SIMPLEX

def ve_tat_ca_diem_dac_trung(khung_hinh, landmarks):
    """Vẽ tất cả 68 điểm đặc trưng trên khuôn mặt"""
    for i in range(68):
        x = landmarks.part(i).x
        y = landmarks.part(i).y
        cv2.circle(khung_hinh, (x, y), 2, (0, 255, 0), -1)

def midpoint(diem_1, diem_2):
    """Tính trung điểm giữa hai điểm đặc trưng"""
    x = (diem_1.x + diem_2.x) / 2
    y = (diem_1.y + diem_2.y) / 2
    return (int(x), int(y))

def get_blinking_ratio(diem_mat, landmarks):
    """Tính tỷ lệ nháy mắt dựa trên các điểm đặc trưng của mắt"""
    diem_trai = (landmarks.part(diem_mat[0]).x, landmarks.part(diem_mat[0]).y)
    diem_phai = (landmarks.part(diem_mat[3]).x, landmarks.part(diem_mat[3]).y)
    trung_diem_tren = midpoint(landmarks.part(diem_mat[1]), landmarks.part(diem_mat[2]))
    trung_diem_duoi = midpoint(landmarks.part(diem_mat[5]), landmarks.part(diem_mat[4]))

    # Vẽ đường ngang và dọc trên mắt để trực quan hóa
    cv2.line(khung_hinh, diem_trai, diem_phai, (0, 255, 0), 2)
    cv2.line(khung_hinh, trung_diem_tren, trung_diem_duoi, (0, 255, 0), 2)

    # Tính chiều dài đường ngang và dọc
    chieu_dai_ngang = hypot((diem_trai[0] - diem_phai[0]), (diem_trai[1] - diem_phai[1]))
    chieu_dai_doc = hypot((trung_diem_tren[0] - trung_diem_duoi[0]), (trung_diem_tren[1] - trung_diem_duoi[1]))

    # Tính tỷ lệ nháy mắt
    ty_le = chieu_dai_ngang / chieu_dai_doc if chieu_dai_doc != 0 else 0
    return ty_le

# Biến làm mượt (EMA) cho chuyển động chuột
x_truoc, y_truoc = None, None
x_lam_muot, y_lam_muot = None, None
he_so_lam_muot = 0.1  # Hệ số làm mượt
do_nhay_x = 29
do_nhay_y = 37
nguong_chuyen_dong = 40
pyautogui.FAILSAFE = False
tam_dung = False

# Biến phát hiện nháy mắt để click
NGUONG_NHAY_MAT = 3.8  # Ngưỡng tỷ lệ để coi là nháy mắt
THOI_GIAN_CLICK = 1  # Thời gian giữ nháy mắt để click (giây)
thoi_diem_nhay_mat_trai = None
thoi_gian_nghi_click = 0.5  # thời gian nghỉ giữa các lần click (giây)
thoi_diem_click_cuoi_trai = 0

# Điểm đặc trưng của mắt trái và mắt phải
DIEM_MAT_TRAI = list(range(36, 42))
DIEM_MAT_PHAI = list(range(42, 48))

while True:
    ret, khung_hinh = cap.read()
    if not ret:
        print("Không thể chụp khung hình")
        break

    khung_hinh = cv2.flip(khung_hinh, 1)
    anh_xam = cv2.cvtColor(khung_hinh, cv2.COLOR_BGR2GRAY)
    
    # Khởi tạo vị trí chuột hiện tại
    vi_tri_chuot_x, vi_tri_chuot_y = pyautogui.position()

    # Bật/tắt tạm dừng bằng phím 'p'
    phim = cv2.waitKey(1) & 0xFF
    if phim == ord('q'):
        break

    if tam_dung:
        cv2.putText(khung_hinh, "STOP", (10, 30), font, 1, (0, 0, 255), 2)
        cv2.imshow("Điều khiển chuột bằng đầu", khung_hinh)
        continue

    mat_khuon_mat = detector(anh_xam)
    if len(mat_khuon_mat) == 0:
        cv2.putText(khung_hinh, "FACE NOT DETECTED", (10, 30), font, 1, (0, 0, 255), 2)
        thoi_diem_nhay_mat_trai = None  # Đặt lại thời điểm nháy mắt trái
    else:
        khuon_mat = mat_khuon_mat[0]  # Lấy khuôn mặt đầunode tiên
        landmarks = predictor(anh_xam, khuon_mat)
        x_mui = landmarks.part(30).x
        y_mui = landmarks.part(30).y

        ve_tat_ca_diem_dac_trung(khung_hinh, landmarks)

        # Làm mượt chuyển động chuột bằng EMA
        if x_lam_muot is None or y_lam_muot is None:
            x_lam_muot, y_lam_muot = x_mui, y_mui
        else:
            x_lam_muot = he_so_lam_muot * x_mui + (1 - he_so_lam_muot) * x_lam_muot
            y_lam_muot = he_so_lam_muot * y_mui + (1 - he_so_lam_muot) * y_lam_muot

        # Di chuyển chuột
        if x_truoc is not None and y_truoc is not None:
            dx = (x_lam_muot - x_truoc) * do_nhay_x
            dy = (y_lam_muot - y_truoc) * do_nhay_y

            if abs(dx) < nguong_chuyen_dong:
                dx = 0
            if abs(dy) < nguong_chuyen_dong:
                dy = 0

            vi_tri_moi_x = max(0, min(chieu_rong_man_hinh - 1, vi_tri_chuot_x + dx))
            vi_tri_moi_y = max(0, min(chieu_cao_man_hinh - 1, vi_tri_chuot_y + dy))
            pyautogui.moveTo(vi_tri_moi_x, vi_tri_moi_y)
            vi_tri_chuot_x, vi_tri_chuot_y = vi_tri_moi_x, vi_tri_moi_y  # Cập nhật vị trí chuột

        x_truoc, y_truoc = x_lam_muot, y_lam_muot

        # Phát hiện nháy mắt
        ty_le_mat_trai = get_blinking_ratio(DIEM_MAT_TRAI, landmarks)
        ty_le_mat_phai = get_blinking_ratio(DIEM_MAT_PHAI, landmarks)
        thoi_diem_hien_tai = time.time()

        # Xử lý nháy mắt trái (click chuột trái)
        if ty_le_mat_trai > NGUONG_NHAY_MAT:
            if thoi_diem_nhay_mat_trai is None:
                thoi_diem_nhay_mat_trai = thoi_diem_hien_tai
            elif (thoi_diem_hien_tai - thoi_diem_nhay_mat_trai) >= THOI_GIAN_CLICK:
                if (thoi_diem_hien_tai - thoi_diem_click_cuoi_trai) >= thoi_gian_nghi_click:
                    pyautogui.click(button='left')
                    thoi_diem_click_cuoi_trai = thoi_diem_hien_tai
                    thoi_diem_nhay_mat_trai = None  # Đặt lại sau khi click 
                    cv2.putText(khung_hinh, "Left Click!", (10, 90), font, 0.7, (0, 255, 0), 2)
            cv2.putText(khung_hinh, "NHAY MAT PHAI", (10, 150), font, 0.7, (255, 0, 0), 2)
        else:
            thoi_diem_nhay_mat_trai = None

        # Hiển thị tỷ lệ nháy mắt để kiểm tra
        cv2.putText(khung_hinh, f"TY LE PHAI: {ty_le_mat_trai:.2f}", (10, 120), font, 0.7, (255, 0, 0), 2)

    # Hiển thị trạng thái
    cv2.putText(khung_hinh, f"TOA DO: ({int(vi_tri_chuot_x)}, {int(vi_tri_chuot_y)})", (10, 60),font, 0.7, (255, 0, 0), 2)
    
    cv2.imshow("Điều khiển chuột bằng đầu", khung_hinh)

cap.release()
cv2.destroyAllWindows()