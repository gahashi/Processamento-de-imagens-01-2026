import numpy as np

try:
    import cv2 as _cv2
except ModuleNotFoundError:
    _cv2 = None


if _cv2 is not None:
    COLOR_BGR2HSV = _cv2.COLOR_BGR2HSV
    COLOR_HSV2BGR = _cv2.COLOR_HSV2BGR
    NORM_MINMAX = _cv2.NORM_MINMAX
    WINDOW_NORMAL = _cv2.WINDOW_NORMAL
    WINDOW_FULLSCREEN = _cv2.WINDOW_FULLSCREEN
    WND_PROP_FULLSCREEN = _cv2.WND_PROP_FULLSCREEN
    FONT_HERSHEY_SIMPLEX = _cv2.FONT_HERSHEY_SIMPLEX

    imread = _cv2.imread
    imwrite = _cv2.imwrite
    cvtColor = _cv2.cvtColor
    split = _cv2.split
    merge = _cv2.merge
    inRange = _cv2.inRange
    bitwise_or = _cv2.bitwise_or
    bitwise_not = _cv2.bitwise_not
    bitwise_and = _cv2.bitwise_and
    normalize = _cv2.normalize
    rectangle = _cv2.rectangle
    putText = _cv2.putText
    namedWindow = _cv2.namedWindow
    setWindowProperty = _cv2.setWindowProperty
    imshow = _cv2.imshow
    waitKey = _cv2.waitKey
    destroyAllWindows = _cv2.destroyAllWindows

else:
    from PIL import Image

    COLOR_BGR2HSV = 40
    COLOR_HSV2BGR = 54
    NORM_MINMAX = 32
    WINDOW_NORMAL = 0
    WINDOW_FULLSCREEN = 1
    WND_PROP_FULLSCREEN = 0
    FONT_HERSHEY_SIMPLEX = 0

    def imread(caminho):
        try:
            img_rgb = Image.open(caminho).convert("RGB")
        except FileNotFoundError:
            return None

        img_rgb = np.array(img_rgb, dtype=np.uint8)
        return img_rgb[:, :, ::-1].copy()

    def imwrite(caminho, img):
        if img.ndim == 2:
            Image.fromarray(img.astype(np.uint8)).save(caminho)
        else:
            img_rgb = img[:, :, ::-1].astype(np.uint8)
            Image.fromarray(img_rgb).save(caminho)

        return True

    def split(img):
        return tuple(img[:, :, i] for i in range(img.shape[2]))

    def merge(canais):
        return np.stack(canais, axis=2).astype(np.uint8)

    def _bgr_para_hsv(img_bgr):
        img_rgb = img_bgr[:, :, ::-1].astype(np.float32) / 255.0

        r = img_rgb[:, :, 0]
        g = img_rgb[:, :, 1]
        b = img_rgb[:, :, 2]

        maximo = np.max(img_rgb, axis=2)
        minimo = np.min(img_rgb, axis=2)
        diferenca = maximo - minimo

        h = np.zeros_like(maximo, dtype=np.float32)
        mascara = diferenca != 0

        idx = (maximo == r) & mascara
        h[idx] = (60.0 * ((g[idx] - b[idx]) / diferenca[idx]) + 360.0) % 360.0

        idx = (maximo == g) & mascara
        h[idx] = 60.0 * ((b[idx] - r[idx]) / diferenca[idx]) + 120.0

        idx = (maximo == b) & mascara
        h[idx] = 60.0 * ((r[idx] - g[idx]) / diferenca[idx]) + 240.0

        s = np.zeros_like(maximo, dtype=np.float32)
        s[maximo != 0] = diferenca[maximo != 0] / maximo[maximo != 0]

        hsv = np.zeros_like(img_bgr, dtype=np.uint8)
        hsv[:, :, 0] = np.clip(h / 2.0, 0, 179).astype(np.uint8)
        hsv[:, :, 1] = np.clip(s * 255.0, 0, 255).astype(np.uint8)
        hsv[:, :, 2] = np.clip(maximo * 255.0, 0, 255).astype(np.uint8)

        return hsv

    def _hsv_para_bgr(img_hsv):
        h = img_hsv[:, :, 0].astype(np.float32) * 2.0
        s = img_hsv[:, :, 1].astype(np.float32) / 255.0
        v = img_hsv[:, :, 2].astype(np.float32) / 255.0

        c = v * s
        x = c * (1 - np.abs((h / 60.0) % 2 - 1))
        m = v - c

        r = np.zeros_like(h)
        g = np.zeros_like(h)
        b = np.zeros_like(h)

        faixas = [
            ((0 <= h) & (h < 60), c, x, 0),
            ((60 <= h) & (h < 120), x, c, 0),
            ((120 <= h) & (h < 180), 0, c, x),
            ((180 <= h) & (h < 240), 0, x, c),
            ((240 <= h) & (h < 300), x, 0, c),
            ((300 <= h) & (h < 360), c, 0, x),
        ]

        for mascara, rv, gv, bv in faixas:
            r[mascara] = rv[mascara] if hasattr(rv, "__getitem__") else rv
            g[mascara] = gv[mascara] if hasattr(gv, "__getitem__") else gv
            b[mascara] = bv[mascara] if hasattr(bv, "__getitem__") else bv

        rgb = np.stack([(r + m), (g + m), (b + m)], axis=2)
        bgr = rgb[:, :, ::-1] * 255.0
        return np.clip(bgr, 0, 255).astype(np.uint8)

    def cvtColor(img, codigo):
        if codigo == COLOR_BGR2HSV:
            return _bgr_para_hsv(img)

        if codigo == COLOR_HSV2BGR:
            return _hsv_para_bgr(img)

        raise ValueError("Codigo de conversao de cor nao suportado.")

    def inRange(img, limite_inferior, limite_superior):
        limite_inferior = np.asarray(limite_inferior, dtype=img.dtype)
        limite_superior = np.asarray(limite_superior, dtype=img.dtype)

        dentro = np.all(
            (img >= limite_inferior) & (img <= limite_superior),
            axis=2
        )

        return np.where(dentro, 255, 0).astype(np.uint8)

    def bitwise_or(a, b):
        return np.bitwise_or(a, b).astype(np.uint8)

    def bitwise_not(a):
        return np.bitwise_not(a).astype(np.uint8)

    def bitwise_and(a, b):
        return np.bitwise_and(a, b).astype(np.uint8)

    def normalize(src, dst, alpha, beta, norm_type):
        src = src.astype(np.float64)
        minimo = np.min(src)
        maximo = np.max(src)

        if maximo == minimo:
            return np.full_like(src, alpha, dtype=np.uint8)

        normalizado = (src - minimo) / (maximo - minimo)
        normalizado = normalizado * (beta - alpha) + alpha

        return np.clip(normalizado, alpha, beta).astype(np.uint8)

    def rectangle(img, pt1, pt2, color, thickness=1):
        x1, y1 = pt1
        x2, y2 = pt2

        x1 = max(0, min(img.shape[1] - 1, x1))
        x2 = max(0, min(img.shape[1] - 1, x2))
        y1 = max(0, min(img.shape[0] - 1, y1))
        y2 = max(0, min(img.shape[0] - 1, y2))

        t = max(1, int(thickness))
        img[y1:y1 + t, x1:x2 + 1] = color
        img[max(y2 - t + 1, 0):y2 + 1, x1:x2 + 1] = color
        img[y1:y2 + 1, x1:x1 + t] = color
        img[y1:y2 + 1, max(x2 - t + 1, 0):x2 + 1] = color

        return img

    def putText(img, text, org, font_face, font_scale, color, thickness=1):
        return img

    def namedWindow(*args, **kwargs):
        return None

    def setWindowProperty(*args, **kwargs):
        return None

    def imshow(*args, **kwargs):
        return None

    def waitKey(*args, **kwargs):
        return 0

    def destroyAllWindows(*args, **kwargs):
        return None
