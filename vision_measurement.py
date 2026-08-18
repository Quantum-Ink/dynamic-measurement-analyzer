import cv2
import numpy as np


# ========================================
# 标准件实际尺寸
# ========================================

REFERENCE_LONG_MM = 68.0
REFERENCE_SHORT_MM = 36.0

IMAGE_PATH = "test_object.jpg"


# ========================================
# 屏幕可用显示区域
# ========================================

MAX_WIDTH = 1400
MAX_HEIGHT = 800


# ========================================
# 保持比例缩放
# ========================================

def resize_keep_ratio(image, max_width, max_height):

    h, w = image.shape[:2]

    scale = min(
        max_width / w,
        max_height / h,
        1.0
    )

    new_w = max(
        1,
        int(w * scale)
    )

    new_h = max(
        1,
        int(h * scale)
    )

    resized = cv2.resize(
        image,
        (new_w, new_h),
        interpolation=cv2.INTER_AREA
    )

    return resized


# ========================================
# 创建比例正确的 OpenCV 窗口
# ========================================

def show_window(name, image):

    display = resize_keep_ratio(
        image,
        MAX_WIDTH,
        MAX_HEIGHT
    )

    h, w = display.shape[:2]

    cv2.namedWindow(
        name,
        cv2.WINDOW_NORMAL |
        cv2.WINDOW_KEEPRATIO
    )

    cv2.resizeWindow(
        name,
        w,
        h
    )

    cv2.imshow(
        name,
        display
    )

    return display


# ========================================
# 读取图片
# ========================================

image = cv2.imread(
    IMAGE_PATH
)

if image is None:

    print(
        "ERROR: Cannot read image."
    )

    raise SystemExit


print()
print("========================================")
print("       Vision Measurement v3.2")
print("========================================")
print()

print(
    f"Original image: "
    f"{image.shape[1]} x {image.shape[0]} px"
)

print()
print(
    "请在完整图片中框选盒子。"
)

print(
    "鼠标左键拖动选择。"
)

print(
    "选择完成后按 ENTER。"
)

print(
    "取消按 ESC。"
)

print()


# ========================================
# 显示完整照片
# ========================================

display_image = show_window(
    "Select Object",
    image
)


# ========================================
# ROI选择
# ========================================

roi = cv2.selectROI(
    "Select Object",
    display_image,
    showCrosshair=True,
    fromCenter=False
)


cv2.destroyWindow(
    "Select Object"
)


x, y, w, h = roi


if w == 0 or h == 0:

    print(
        "No ROI selected."
    )

    raise SystemExit


# ========================================
# ROI
# ========================================

roi_image = display_image[
    y:y+h,
    x:x+w
]


if roi_image.size == 0:

    print(
        "ERROR: Empty ROI."
    )

    raise SystemExit


# ========================================
# 灰度
# ========================================

gray = cv2.cvtColor(
    roi_image,
    cv2.COLOR_BGR2GRAY
)


# ========================================
# 高斯滤波
# ========================================

blur = cv2.GaussianBlur(
    gray,
    (5, 5),
    0
)


# ========================================
# OTSU
# ========================================

_, binary = cv2.threshold(
    blur,
    0,
    255,
    cv2.THRESH_BINARY +
    cv2.THRESH_OTSU
)


# ========================================
# 形态学处理
# ========================================

kernel = np.ones(
    (5, 5),
    np.uint8
)


binary = cv2.morphologyEx(
    binary,
    cv2.MORPH_CLOSE,
    kernel,
    iterations=2
)


binary = cv2.morphologyEx(
    binary,
    cv2.MORPH_OPEN,
    kernel,
    iterations=1
)


# ========================================
# 查找轮廓
# ========================================

contours, _ = cv2.findContours(
    binary,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE
)


if len(contours) == 0:

    print(
        "No object detected."
    )

    show_window(
        "Binary",
        binary
    )

    cv2.waitKey(0)
    cv2.destroyAllWindows()

    raise SystemExit


# ========================================
# 最大轮廓
# ========================================

largest = max(
    contours,
    key=cv2.contourArea
)


# ========================================
# 旋转矩形
# ========================================

rotated_rect = cv2.minAreaRect(
    largest
)


(center_x, center_y), \
(width_px, height_px), \
angle = rotated_rect


# ========================================
# 长短边
# ========================================

pixel_long = max(
    width_px,
    height_px
)

pixel_short = min(
    width_px,
    height_px
)


# ========================================
# 比例
# ========================================

pixels_per_mm_long = (
    pixel_long /
    REFERENCE_LONG_MM
)

pixels_per_mm_short = (
    pixel_short /
    REFERENCE_SHORT_MM
)


# ========================================
# 测量
# ========================================

measured_long = (
    pixel_long /
    pixels_per_mm_long
)

measured_short = (
    pixel_short /
    pixels_per_mm_short
)


# ========================================
# 输出
# ========================================

print()
print(
    "========================================"
)

print(
    "        Measurement Result"
)

print(
    "========================================"
)

print(
    f"Reference Size : "
    f"{REFERENCE_LONG_MM:.2f} x "
    f"{REFERENCE_SHORT_MM:.2f} mm"
)

print()

print(
    f"Pixel Long     : "
    f"{pixel_long:.2f} px"
)

print(
    f"Pixel Short    : "
    f"{pixel_short:.2f} px"
)

print()

print(
    f"Scale Long     : "
    f"{pixels_per_mm_long:.4f} px/mm"
)

print(
    f"Scale Short    : "
    f"{pixels_per_mm_short:.4f} px/mm"
)

print()

print(
    f"Measured Long  : "
    f"{measured_long:.3f} mm"
)

print(
    f"Measured Short : "
    f"{measured_short:.3f} mm"
)

print()

print(
    f"Rotation Angle : "
    f"{angle:.2f} degree"
)

print(
    "========================================"
)


# ========================================
# 绘制检测结果
# ========================================

result = roi_image.copy()


box = cv2.boxPoints(
    rotated_rect
)

box = np.int32(
    box
)


cv2.drawContours(
    result,
    [box],
    0,
    (0, 255, 0),
    3
)


# ========================================
# 文字
# ========================================

cv2.putText(
    result,
    f"Long: {measured_long:.2f} mm",
    (20, 40),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.8,
    (0, 255, 0),
    2
)


cv2.putText(
    result,
    f"Short: {measured_short:.2f} mm",
    (20, 75),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.8,
    (0, 255, 0),
    2
)


# ========================================
# 显示结果
# ========================================

show_window(
    "Measurement Result",
    result
)


show_window(
    "Binary",
    binary
)


cv2.waitKey(0)

cv2.destroyAllWindows()