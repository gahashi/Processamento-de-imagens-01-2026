import cv2
import numpy as np


def converter_cinza(img):
    """
    Converte uma imagem BGR para escala de cinza usando média ponderada.
    """

    if len(img.shape) == 2:
        return img

    b, g, r = cv2.split(img)

    img_cinza = 0.299 * b + 0.587 * g + 0.114 * r
    img_cinza = np.array(img_cinza, dtype=np.uint8)

    return img_cinza


def calcular_fft(img_cinza):
    """
    Calcula a FFT da imagem em escala de cinza.
    """

    f = np.fft.fft2(img_cinza)
    fshift = np.fft.fftshift(f)

    return fshift


def calcular_espectro_magnitude(fshift):
    """
    Calcula o espectro de magnitude para visualização.
    """

    magnitude = 20 * np.log(np.abs(fshift) + 0.00001)
    magnitude = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)
    magnitude = np.array(magnitude, dtype=np.uint8)

    return magnitude


def criar_mascara_passa_baixa(altura, largura, raio):
    """
    Cria uma máscara circular passa-baixa no domínio da frequência.

    Frequências próximas ao centro são preservadas.
    Frequências distantes são removidas.
    """

    mascara = np.zeros((altura, largura), dtype=np.uint8)

    centro_y = altura // 2
    centro_x = largura // 2

    for y in range(altura):
        for x in range(largura):
            distancia = np.sqrt((x - centro_x) ** 2 + (y - centro_y) ** 2)

            if distancia <= raio:
                mascara[y, x] = 1

    return mascara


def criar_mascara_passa_alta(altura, largura, raio):
    """
    Cria uma máscara circular passa-alta no domínio da frequência.

    Frequências próximas ao centro são removidas.
    Frequências distantes são preservadas.
    """

    mascara = np.ones((altura, largura), dtype=np.uint8)

    centro_y = altura // 2
    centro_x = largura // 2

    for y in range(altura):
        for x in range(largura):
            distancia = np.sqrt((x - centro_x) ** 2 + (y - centro_y) ** 2)

            if distancia <= raio:
                mascara[y, x] = 0

    return mascara


def aplicar_mascara_frequencia(img_cinza, mascara):
    """
    Aplica uma máscara no domínio da frequência e retorna a imagem filtrada.
    """

    fshift = calcular_fft(img_cinza)

    fshift_filtrado = fshift * mascara

    ishift = np.fft.ifftshift(fshift_filtrado)
    img_back = np.fft.ifft2(ishift)
    img_back = np.abs(img_back)

    img_back = cv2.normalize(img_back, None, 0, 255, cv2.NORM_MINMAX)
    img_back = np.array(img_back, dtype=np.uint8)

    return img_back


def aplicar_passa_baixa(img_cinza, raio=40):
    """
    Aplica filtro passa-baixa ideal.
    """

    altura, largura = img_cinza.shape

    mascara = criar_mascara_passa_baixa(
        altura,
        largura,
        raio
    )

    img_filtrada = aplicar_mascara_frequencia(img_cinza, mascara)

    return img_filtrada, mascara


def aplicar_passa_alta(img_cinza, raio=40):
    """
    Aplica filtro passa-alta ideal.
    """

    altura, largura = img_cinza.shape

    mascara = criar_mascara_passa_alta(
        altura,
        largura,
        raio
    )

    img_filtrada = aplicar_mascara_frequencia(img_cinza, mascara)

    return img_filtrada, mascara


def aplicar_frequencia_no_canal_v(img_bgr, tipo="passa_baixa", raio=40):
    """
    Aplica filtragem no domínio da frequência no canal V do HSV.

    Essa abordagem mantém a informação de cor,
    mas suaviza a intensidade/brilho da imagem.
    """

    img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

    h, s, v = cv2.split(img_hsv)

    espectro = calcular_espectro_magnitude(calcular_fft(v))

    if tipo == "passa_baixa":
        v_filtrado, mascara_freq = aplicar_passa_baixa(v, raio)

    elif tipo == "passa_alta":
        v_filtrado, mascara_freq = aplicar_passa_alta(v, raio)

    else:
        print("Filtro de frequência desconhecido:", tipo)
        return img_bgr, espectro, None

    img_hsv_filtrada = cv2.merge([h, s, v_filtrado])
    img_bgr_filtrada = cv2.cvtColor(img_hsv_filtrada, cv2.COLOR_HSV2BGR)

    mascara_freq_visivel = np.array(mascara_freq * 255, dtype=np.uint8)

    return img_bgr_filtrada, espectro, mascara_freq_visivel


def aplicar_filtros_frequencia(img, lista_filtros):
    """
    Aplica uma lista de filtros no domínio da frequência.

    Exemplo:
    {
        "tipo": "passa_baixa",
        "raio": 40,
        "canal": "v"
    }
    """

    img_saida = img.copy()
    resultados = {}

    for filtro in lista_filtros:
        tipo = filtro.get("tipo", "passa_baixa")
        raio = filtro.get("raio", 40)
        canal = filtro.get("canal", "v")

        if canal == "v":
            img_saida, espectro, mascara_freq = aplicar_frequencia_no_canal_v(
                img_saida,
                tipo=tipo,
                raio=raio
            )

            resultados["espectro_" + tipo] = espectro

            if mascara_freq is not None:
                resultados["mascara_frequencia_" + tipo] = mascara_freq

        elif canal == "cinza":
            img_cinza = converter_cinza(img_saida)
            espectro = calcular_espectro_magnitude(calcular_fft(img_cinza))

            if tipo == "passa_baixa":
                img_filtrada, mascara_freq = aplicar_passa_baixa(img_cinza, raio)

            elif tipo == "passa_alta":
                img_filtrada, mascara_freq = aplicar_passa_alta(img_cinza, raio)

            else:
                print("Filtro de frequência desconhecido:", tipo)
                continue

            resultados["frequencia_cinza_" + tipo] = img_filtrada
            resultados["espectro_" + tipo] = espectro
            resultados["mascara_frequencia_" + tipo] = np.array(mascara_freq * 255, dtype=np.uint8)

        else:
            print("Canal de frequência desconhecido:", canal)

    return img_saida, resultados