import cv2
import numpy as np
import math

def angle(pt1, pt2, pt0):
    pt1 = np.array(pt1, dtype=np.float64)
    pt2 = np.array(pt2, dtype=np.float64)
    pt0 = np.array(pt0, dtype=np.float64)
    
    dx1 = pt1[0] - pt0[0]
    dy1 = pt1[1] - pt0[1]
    dx2 = pt2[0] - pt0[0]
    dy2 = pt2[1] - pt0[1]

    numerator = dx1 * dx2 + dy1 * dy2
    denominator = math.sqrt(max(dx1*dx1 + dy1*dy1, 1e-10) * max(dx2*dx2 + dy2*dy2, 1e-10))
    if denominator == 0:
        return 0
    cos_angle = numerator / denominator
    cos_angle = max(min(cos_angle, 1), -1)
    return cos_angle

def find_squares(img):
    squares = []
    img_blur = cv2.medianBlur(img, 9)
    for c in range(3):
        ch = img_blur[:,:,c]
        gray = ch.copy()
        for l in range(2):
            if l == 0:
                edges = cv2.Canny(gray, 10, 30)
                edges = cv2.dilate(edges, None)
            else:
                _, edges = cv2.threshold(gray, (l+1)*255/2, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                cnt_len = cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, 0.02*cnt_len, True)
                if len(approx) == 4 and cv2.isContourConvex(approx):
                    area = abs(cv2.contourArea(approx))
                    if area > 1000:
                        max_cos = 0
                        pts = approx.reshape(4, 2).astype(np.float64)
                        for j in range(4):
                            cos = abs(angle(pts[j], pts[(j+2)%4], pts[(j+1)%4]))
                            max_cos = max(max_cos, cos)
                        if max_cos < 0.3:
                            squares.append(approx)
    return squares

def find_biggest_square(squares, img_shape):
    h, w = img_shape[:2]
    min_area = 0.8 * h * w  # mínimo área: 50% de la imagen (ajusta según necesidad)

    max_area = 0
    max_sq = None
    for sq in squares:
        area = cv2.contourArea(sq)
        if area > max_area:
            max_area = area
            max_sq = sq

    if max_area < min_area or max_sq is None:
        # No hay cuadrado suficientemente grande: usa toda la imagen
        return np.array([[0,0],[w,0],[w,h],[0,h]], dtype=np.float32)
    return max_sq.reshape(4,2).astype(np.float32)


def scan_image(img, pts):
    # ordena puntos en tl, tr, br, bl (top-left, top-right, bottom-right, bottom-left)
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    maxWidth = max(int(widthA), int(widthB))

    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxHeight = max(int(heightA), int(heightB))

    dst = np.array([
        [0, 0],
        [maxWidth-1, 0],
        [maxWidth-1, maxHeight-1],
        [0, maxHeight-1]], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(img, M, (maxWidth, maxHeight))

    return warped

def order_points(pts):
    # Ordenar los puntos en sentido tl, tr, br, bl
    rect = np.zeros((4, 2), dtype = "float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    return rect

if __name__ == "__main__":
    img = cv2.imread(r"D:\Tesis\docx\1.png")
    if img is None:
        print("No se pudo cargar la imagen")
        exit()

    squares = find_squares(img)
    biggest = find_biggest_square(squares, img.shape)

    print("Puntos del cuadrado más grande:", biggest)

    scanned = scan_image(img, biggest)

    gray_scanned = cv2.cvtColor(scanned, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(
        gray_scanned, 255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 15, 4
    )
    thresh = cv2.adaptiveThreshold(
    gray_scanned, 255,
    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    cv2.THRESH_BINARY, 15, 4  # bloque mayor y C un poco mayor
    )
    cv2.imshow("Original", img)
    cv2.imshow("Escaneado", scanned)
    cv2.imshow("Escaneado - Binarizado", thresh)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
# Ejemplo
input_image = r"D:\Tesis\docx\2.jpg"
output_image = r"D:\Tesis\docx\1_output.png"


