import numpy as np


def criar_mascara_circular(altura, largura, centro_x, centro_y, raio):
    """
    Cria uma máscara circular.
    Pixels dentro do círculo recebem 255.
    Pixels fora do círculo recebem 0.
    """

    mascara = np.zeros((altura, largura), dtype=np.uint8)

    for y in range(altura):
        for x in range(largura):
            distancia = np.sqrt((x - centro_x) ** 2 + (y - centro_y) ** 2)

            if distancia <= raio:
                mascara[y, x] = 255

    return mascara


def aplicar_mascara_circular(img, mascara):
    """
    Aplica uma máscara circular em imagem colorida ou escala de cinza.
    """

    img_saida = np.zeros_like(img)

    if len(img.shape) == 2:
        img_saida[mascara == 255] = img[mascara == 255]
    else:
        img_saida[mascara == 255] = img[mascara == 255]

    return img_saida


def detectar_roi_circular_por_limiar(img, limiar=20, margem=25):
    """
    Detecta automaticamente uma ROI circular aproximada.

    A ideia é:
    1. Converter a imagem para uma intensidade simples.
    2. Encontrar os pixels que não são fundo escuro.
    3. Calcular uma caixa envolvendo essa região.
    4. Estimar centro e raio do círculo.
    5. Reduzir um pouco o raio usando margem.
    """

    altura, largura = img.shape[:2]

    # Converte para uma imagem de intensidade simples sem usar cv2
    if len(img.shape) == 3:
        gray = (
            0.114 * img[:, :, 0] +
            0.587 * img[:, :, 1] +
            0.299 * img[:, :, 2]
        ).astype(np.uint8)
    else:
        gray = img.copy()

    # Pega pixels acima do limiar, ignorando regiões muito escuras
    ys, xs = np.where(gray > limiar)

    if len(xs) == 0 or len(ys) == 0:
        centro_x = largura // 2
        centro_y = altura // 2
        raio = min(altura, largura) // 2
    else:
        x_min = np.min(xs)
        x_max = np.max(xs)
        y_min = np.min(ys)
        y_max = np.max(ys)

        centro_x = int((x_min + x_max) / 2)
        centro_y = int((y_min + y_max) / 2)

        largura_regiao = x_max - x_min
        altura_regiao = y_max - y_min

        raio = int(min(largura_regiao, altura_regiao) / 2)

    # Reduz um pouco para evitar pegar borda externa/reflexos
    raio = raio - margem

    if raio < 1:
        raio = 1

    mascara_roi = criar_mascara_circular(
        altura,
        largura,
        centro_x,
        centro_y,
        raio
    )

    img_roi = aplicar_mascara_circular(img, mascara_roi)

    return img_roi, mascara_roi, centro_x, centro_y, raio