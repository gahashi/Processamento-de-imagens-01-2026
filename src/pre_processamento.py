from src import cv2_compat as cv2
import numpy as np


def converter_hsv(img):
    """
    Converte imagem BGR para HSV.
    O OpenCV carrega imagens no padrão BGR.
    """
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    return img_hsv


def separar_canais_hsv(img_hsv):
    """
    Separa os canais HSV.
    H = matiz/cor
    S = saturação
    V = brilho
    """
    h, s, v = cv2.split(img_hsv)
    return h, s, v


def criar_mascara_hsv(img_hsv, h_min, h_max, s_min, s_max, v_min, v_max):
    """
    Cria uma máscara binária usando uma faixa HSV.
    Pixels dentro da faixa ficam brancos.
    Pixels fora da faixa ficam pretos.
    """

    limite_inferior = np.array([h_min, s_min, v_min])
    limite_superior = np.array([h_max, s_max, v_max])

    mascara = cv2.inRange(img_hsv, limite_inferior, limite_superior)

    return mascara


def combinar_mascaras(lista_mascaras):
    """
    Combina várias máscaras binárias.
    Se o pixel for branco em qualquer máscara, ele fica branco na máscara final.
    """

    mascara_final = np.zeros_like(lista_mascaras[0])

    for mascara in lista_mascaras:
        mascara_final = cv2.bitwise_or(mascara_final, mascara)

    return mascara_final


def subtrair_mascara(mascara_base, mascara_remover):
    """
    Remove da máscara base os pixels presentes na máscara de remoção.
    """

    mascara_remover_invertida = cv2.bitwise_not(mascara_remover)
    mascara_saida = cv2.bitwise_and(mascara_base, mascara_remover_invertida)

    return mascara_saida


def criar_mascaras_por_faixas_hsv(img_hsv, faixas):
    """
    Recebe uma lista de faixas HSV e cria uma máscara para cada item.

    Cada item da lista deve ter:
    - nome
    - h_min, h_max
    - s_min, s_max
    - v_min, v_max
    """

    mascaras = {}

    for faixa in faixas:
        nome = faixa["nome"]

        mascara = criar_mascara_hsv(
            img_hsv,
            faixa["h_min"],
            faixa["h_max"],
            faixa["s_min"],
            faixa["s_max"],
            faixa["v_min"],
            faixa["v_max"]
        )

        mascaras[nome] = mascara

    return mascaras

def criar_mascara_objeto_por_faixas(img_hsv, faixas_objeto, faixas_fundo=None):
    """
    Cria a máscara inicial do objeto de interesse usando uma lista de faixas positivas.

    Neste projeto, o objeto de interesse é o grão/semente.
    As faixas positivas representam:
    - grão amarelo/laranja
    - manchas escuras pertencentes ao grão

    As faixas de fundo são opcionais e podem ser usadas para remoção.
    """

    mascaras_objeto = criar_mascaras_por_faixas_hsv(img_hsv, faixas_objeto)
    mascara_objeto = combinar_mascaras(list(mascaras_objeto.values()))

    mascaras_fundo = {}

    if faixas_fundo is not None:
        mascaras_fundo = criar_mascaras_por_faixas_hsv(img_hsv, faixas_fundo)
        mascara_fundo = combinar_mascaras(list(mascaras_fundo.values()))

        # remove fundo detectado da máscara do objeto
        mascara_objeto = subtrair_mascara(mascara_objeto, mascara_fundo)

    return mascara_objeto, mascaras_objeto, mascaras_fundo
