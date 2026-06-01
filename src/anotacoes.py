import xml.etree.ElementTree as ET
import numpy as np
import cv2


def ler_anotacoes_xml(caminho_xml):
    """
    Lê um arquivo XML no formato Pascal VOC.

    Retorna uma lista de objetos anotados, contendo:
    - nome da classe
    - coordenadas da bounding box
    """

    tree = ET.parse(caminho_xml)
    root = tree.getroot()

    anotacoes = []

    for obj in root.findall("object"):
        nome = obj.find("name").text

        bndbox = obj.find("bndbox")

        xmin = int(float(bndbox.find("xmin").text))
        ymin = int(float(bndbox.find("ymin").text))
        xmax = int(float(bndbox.find("xmax").text))
        ymax = int(float(bndbox.find("ymax").text))

        anotacoes.append({
            "nome": nome,
            "xmin": xmin,
            "ymin": ymin,
            "xmax": xmax,
            "ymax": ymax
        })

    return anotacoes


def contar_anotacoes(anotacoes):
    """
    Conta quantas anotações existem por classe.
    Exemplo:
    yes: 10
    no: 5
    """

    contagem = {}

    for anotacao in anotacoes:
        nome = anotacao["nome"]

        if nome not in contagem:
            contagem[nome] = 0

        contagem[nome] += 1

    return contagem


def criar_mascara_bbox(altura, largura, anotacoes, classe_interesse=None):
    """
    Cria uma máscara binária preenchendo as bounding boxes.

    Se classe_interesse for None, usa todas as classes.
    Se classe_interesse for 'yes', usa somente objetos anotados como yes.
    """

    mascara = np.zeros((altura, largura), dtype=np.uint8)

    for anotacao in anotacoes:
        nome = anotacao["nome"]

        if classe_interesse is not None and nome != classe_interesse:
            continue

        xmin = anotacao["xmin"]
        ymin = anotacao["ymin"]
        xmax = anotacao["xmax"]
        ymax = anotacao["ymax"]

        # Garante que as coordenadas não saiam da imagem
        xmin = max(0, xmin)
        ymin = max(0, ymin)
        xmax = min(largura - 1, xmax)
        ymax = min(altura - 1, ymax)

        mascara[ymin:ymax, xmin:xmax] = 255

    return mascara


def desenhar_bounding_boxes(img, anotacoes):
    """
    Desenha as bounding boxes na imagem.

    Classe yes: verde
    Classe no: vermelho
    """

    img_saida = img.copy()

    for anotacao in anotacoes:
        nome = anotacao["nome"]

        xmin = anotacao["xmin"]
        ymin = anotacao["ymin"]
        xmax = anotacao["xmax"]
        ymax = anotacao["ymax"]

        if nome == "yes":
            cor = (0, 255, 0)
        else:
            cor = (0, 0, 255)

        cv2.rectangle(
            img_saida,
            (xmin, ymin),
            (xmax, ymax),
            cor,
            2
        )

        cv2.putText(
            img_saida,
            nome,
            (xmin, max(0, ymin - 5)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            cor,
            2
        )

    return img_saida


def calcular_iou_bbox(mascara_predita, mascara_referencia):
    """
    Calcula IoU entre a máscara gerada pelo algoritmo e a máscara de referência.
    A referência aqui pode ser a máscara aproximada criada a partir das bounding boxes.
    """

    pred = mascara_predita > 0
    ref = mascara_referencia > 0

    intersecao = np.logical_and(pred, ref).sum()
    uniao = np.logical_or(pred, ref).sum()

    if uniao == 0:
        return 0

    return intersecao / uniao


def calcular_dice_bbox(mascara_predita, mascara_referencia):
    """
    Calcula Dice entre a máscara gerada pelo algoritmo e a máscara de referência.
    """

    pred = mascara_predita > 0
    ref = mascara_referencia > 0

    intersecao = np.logical_and(pred, ref).sum()
    soma = pred.sum() + ref.sum()

    if soma == 0:
        return 0

    return (2 * intersecao) / soma