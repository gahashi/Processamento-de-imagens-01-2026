import os
import cv2


def carregar_imagem(caminho):
    img = cv2.imread(caminho)

    if img is None:
        raise ValueError(f"Erro ao carregar a imagem: {caminho}")

    return img


def salvar_imagem(caminho, img):
    pasta = os.path.dirname(caminho)

    if pasta != "":
        os.makedirs(pasta, exist_ok=True)

    cv2.imwrite(caminho, img)

def mostrar_imagem(nome, img):
    cv2.namedWindow(nome, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(nome, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    cv2.imshow(nome, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()