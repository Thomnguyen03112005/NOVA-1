import cv2
import os

ref_point = []
cropping = False

def click_and_crop(event, x, y, flags, param):
    global ref_point, cropping
    if event == cv2.EVENT_LBUTTONDOWN:
        ref_point = [(x, y)]
        cropping = True
    elif event == cv2.EVENT_LBUTTONUP:
        ref_point.append((x, y))
        cropping = False
        cv2.rectangle(image, ref_point[0], ref_point[1], (0, 255, 0), 2)
        cv2.imshow("Image", image)

image_path = "f:/nova/image/khodo.png"

if not os.path.exists(image_path):
    print("❌ File KHÔNG tồn tại!")
    exit()

image = cv2.imread(image_path)
if image is None:
    print("❌ OpenCV KHÔNG đọc được ảnh!")
    exit()

clone = image.copy()
cv2.namedWindow("Image")
cv2.setMouseCallback("Image", click_and_crop)

print("🖱️ Dùng chuột kéo chọn vùng -> nhấn 'c' để cắt, 'r' để chọn lại.")

while True:
    cv2.imshow("Image", image)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("r"):
        image = clone.copy()
        ref_point = []
    elif key == ord("c"):
        break

cv2.destroyAllWindows()

if len(ref_point) == 2:
    x1, y1 = ref_point[0]
    x2, y2 = ref_point[1]
    roi = clone[min(y1,y2):max(y1,y2), min(x1,x2):max(x1,x2)]
    cv2.imshow("Cropped", roi)
    output_path = "f:/nova/output_crop.jpg"
    cv2.imwrite(output_path, roi)
    print(f"✅ Đã cắt và lưu ảnh tại: {output_path}")
    print(f"📍 Tọa độ: ({min(x1,x2)}, {min(y1,y2)}) đến ({max(x1,x2)}, {max(y1,y2)})")
    cv2.waitKey(0)
else:
    print("⚠️ Bạn chưa chọn vùng hợp lệ để cắt!")
