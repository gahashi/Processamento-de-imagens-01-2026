import os
import numpy as np

from src.pos_processamento import contar_componentes


def calcular_iou(mascara_predita, mascara_referencia):
    """
    Calcula IoU entre duas máscaras binárias.

    IoU = interseção / união
    """

    pred = mascara_predita > 0
    ref = mascara_referencia > 0

    intersecao = np.logical_and(pred, ref).sum()
    uniao = np.logical_or(pred, ref).sum()

    if uniao == 0:
        return 0

    return intersecao / uniao


def calcular_dice(mascara_predita, mascara_referencia):
    """
    Calcula Dice Coefficient entre duas máscaras binárias.

    Dice = 2 * interseção / soma das áreas
    """

    pred = mascara_predita > 0
    ref = mascara_referencia > 0

    intersecao = np.logical_and(pred, ref).sum()
    soma = pred.sum() + ref.sum()

    if soma == 0:
        return 0

    return (2 * intersecao) / soma


def contar_anotacoes_classe(anotacoes, classe_interesse=None):
    """
    Conta quantas anotações existem para uma determinada classe.

    Se classe_interesse for None, conta todas as classes.
    """

    total = 0

    for anotacao in anotacoes:
        if classe_interesse is None:
            total += 1
        elif anotacao["nome"] == classe_interesse:
            total += 1

    return total


def calcular_erro_contagem(total_detectado, total_anotado):
    """
    Calcula erro absoluto e erro percentual da contagem.
    """

    erro_absoluto = abs(total_detectado - total_anotado)

    if total_anotado == 0:
        erro_percentual = 0
    else:
        erro_percentual = (erro_absoluto / total_anotado) * 100

    return erro_absoluto, erro_percentual


def salvar_metricas(
    pasta_saida,
    nome_base,
    mascara_predita,
    mascara_referencia=None,
    anotacoes=None,
    classe_interesse=None,
    area_minima_contagem=1
):
    """
    Calcula e salva as métricas do resultado.

    Métricas salvas:
    - total de segmentos detectados
    - total anotado no XML
    - diferença de contagem
    - erro percentual da contagem
    - IoU aproximado
    - Dice aproximado
    """

    caminho_metricas = os.path.join(
        pasta_saida,
        "metricas_" + nome_base + ".txt"
    )

    total_detectado = contar_componentes(
        mascara_predita,
        area_minima=area_minima_contagem
    )

    total_anotado = None
    erro_absoluto = None
    erro_percentual = None
    iou = None
    dice = None

    if anotacoes is not None:
        total_anotado = contar_anotacoes_classe(
            anotacoes,
            classe_interesse
        )

        erro_absoluto, erro_percentual = calcular_erro_contagem(
            total_detectado,
            total_anotado
        )

    if mascara_referencia is not None:
        iou = calcular_iou(
            mascara_predita,
            mascara_referencia
        )

        dice = calcular_dice(
            mascara_predita,
            mascara_referencia
        )

    with open(caminho_metricas, "w", encoding="utf-8") as arquivo:
        arquivo.write("Imagem: " + nome_base + "\n")
        arquivo.write("\n")

        arquivo.write("Métrica de contagem de segmentos\n")
        arquivo.write("Total detectado: " + str(total_detectado) + "\n")

        if total_anotado is not None:
            arquivo.write("Total anotado XML: " + str(total_anotado) + "\n")
            arquivo.write("Erro absoluto da contagem: " + str(erro_absoluto) + "\n")
            arquivo.write("Erro percentual da contagem: " + str(round(erro_percentual, 2)) + "%\n")

        arquivo.write("\n")

        arquivo.write("Métricas de sobreposição\n")

        if iou is not None:
            arquivo.write("IoU aproximado: " + str(round(iou, 4)) + "\n")
        else:
            arquivo.write("IoU aproximado: não calculado\n")

        if dice is not None:
            arquivo.write("Dice aproximado: " + str(round(dice, 4)) + "\n")
        else:
            arquivo.write("Dice aproximado: não calculado\n")

        arquivo.write("\n")
        arquivo.write("Observação:\n")
        arquivo.write(
            "As métricas IoU e Dice são aproximadas quando a referência é gerada por bounding boxes, "
            "pois as caixas do XML não representam exatamente o contorno real dos grãos.\n"
        )

    return caminho_metricas