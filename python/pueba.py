import cv2
import numpy as np

def scan_document(image_path, output_path=None):
    image = cv2.imread(image_path)
    if image is None:
        raise Exception(f"No se pudo cargar la imagen desde: {image_path}")
        
    orig = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 9)

    edges = cv2.Canny(gray, 10, 30)
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    max_area = 0
    best_cnt = None
    for cnt in contours:
        approx = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)
        if len(approx) == 4 and cv2.isContourConvex(approx):
            area = cv2.contourArea(approx)
            if area > max_area:
                max_area = area
                best_cnt = approx

    if best_cnt is None:
        raise Exception("No se encontró una forma cuadrada.")

    pts = best_cnt.reshape(4, 2)
    rect = np.zeros((4, 2), dtype="float32")

    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]  # top-left
    rect[2] = pts[np.argmax(s)]  # bottom-right

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # top-right
    rect[3] = pts[np.argmax(diff)]  # bottom-left

    (tl, tr, br, bl) = rect

    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)

    maxWidth = int(max(widthA, widthB))
    maxHeight = int(max(heightA, heightB))

    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]
    ], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(orig, M, (maxWidth, maxHeight))

    if output_path:
        cv2.imwrite(output_path, warped)
        print(f"Imagen escaneada guardada en: {output_path}")

    return warped

# === Entrada y salida ===
if __name__ == "__main__":
    input_path = r"D:\Tesis\docx\1.png"
    output_path = r"D:\Tesis\docx\1_output.png"
    
    try:
        scan_document(input_path, output_path)
    except Exception as e:
        print(f"Error: {e}")
