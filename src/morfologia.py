import numpy as np

try:
    from PIL import Image, ImageFilter
except ModuleNotFoundError:
    Image = None
    ImageFilter = None


def criar_elemento_estruturante(tamanho=3, formato="quadrado"):
    """
    Cria um elemento estruturante para operações morfológicas.

    formato:
    - quadrado: todos os pixels do kernel valem 1
    - cruz: apenas centro, vertical e horizontal valem 1
    - elipse: aproximação de uma elipse dentro do kernel
    """

    elemento = np.zeros((tamanho, tamanho), dtype=np.uint8)

    if formato == "quadrado":
        elemento[:, :] = 1

    elif formato == "cruz":
        centro = tamanho // 2

        for i in range(tamanho):
            elemento[centro, i] = 1
            elemento[i, centro] = 1

    elif formato == "elipse":
        centro = tamanho // 2

        raio_y = tamanho / 2
        raio_x = tamanho / 2

        for y in range(tamanho):
            for x in range(tamanho):
                dy = y - centro
                dx = x - centro

                valor = (dx * dx) / (raio_x * raio_x) + (dy * dy) / (raio_y * raio_y)

                if valor <= 1:
                    elemento[y, x] = 1

    else:
        print("Formato desconhecido. Usando quadrado.")
        elemento[:, :] = 1

    return elemento



def criar_borda_zeros(img, tamanho_borda):
    """
    Cria uma borda de zeros ao redor da imagem.
    Usado para permitir a aplicação da morfologia nas bordas.
    """

    altura, largura = img.shape

    img_borda = np.zeros(
        (altura + 2 * tamanho_borda, largura + 2 * tamanho_borda),
        dtype=img.dtype
    )

    img_borda[
        tamanho_borda:tamanho_borda + altura,
        tamanho_borda:tamanho_borda + largura
    ] = img

    return img_borda


def erosao(img, elemento):
    """
    Aplica erosão manual em uma imagem binária.

    A erosão mantém o pixel branco apenas se todos os pixels
    cobertos pelo elemento estruturante também forem brancos.
    """

    tamanho = elemento.shape[0]

    if Image is not None and np.all(elemento == 1):
        return np.array(
            Image.fromarray(img).filter(ImageFilter.MinFilter(tamanho)),
            dtype=np.uint8
        )

    altura, largura = img.shape
    borda = tamanho // 2

    img_borda = criar_borda_zeros(img, borda)
    img_saida = np.zeros_like(img)

    for y in range(altura):
        for x in range(largura):
            regiao = img_borda[
                y:y + tamanho,
                x:x + tamanho
            ]

            manter_pixel = True

            for i in range(tamanho):
                for j in range(tamanho):
                    if elemento[i, j] == 1 and regiao[i, j] == 0:
                        manter_pixel = False

            if manter_pixel:
                img_saida[y, x] = 255

    return img_saida


def dilatacao(img, elemento):
    """
    Aplica dilatação manual em uma imagem binária.

    A dilatação deixa o pixel branco se pelo menos um pixel branco
    da região coincidir com o elemento estruturante.
    """

    tamanho = elemento.shape[0]

    if Image is not None and np.all(elemento == 1):
        return np.array(
            Image.fromarray(img).filter(ImageFilter.MaxFilter(tamanho)),
            dtype=np.uint8
        )

    altura, largura = img.shape
    borda = tamanho // 2

    img_borda = criar_borda_zeros(img, borda)
    img_saida = np.zeros_like(img)

    for y in range(altura):
        for x in range(largura):
            regiao = img_borda[
                y:y + tamanho,
                x:x + tamanho
            ]

            encontrou_pixel = False

            for i in range(tamanho):
                for j in range(tamanho):
                    if elemento[i, j] == 1 and regiao[i, j] > 0:
                        encontrou_pixel = True

            if encontrou_pixel:
                img_saida[y, x] = 255

    return img_saida


def abertura(img, elemento):
    """
    Aplica abertura morfológica.

    Abertura = erosão seguida de dilatação.
    Serve para remover pequenos ruídos brancos.
    """

    img_erosao = erosao(img, elemento)
    img_abertura = dilatacao(img_erosao, elemento)

    return img_abertura


def fechamento(img, elemento):
    """
    Aplica fechamento morfológico.

    Fechamento = dilatação seguida de erosão.
    Serve para fechar pequenos buracos e falhas.
    """

    img_dilatacao = dilatacao(img, elemento)
    img_fechamento = erosao(img_dilatacao, elemento)

    return img_fechamento


def aplicar_morfologia(img, lista_operacoes):
    """
    Aplica uma lista de operações morfológicas na imagem.

    Exemplo de configuração:
    {
        "tipo": "abertura",
        "tamanho": 3,
        "formato": "quadrado"
    }
    """

    img_saida = img.copy()

    for operacao in lista_operacoes:
        tipo = operacao["tipo"]
        tamanho = operacao.get("tamanho", 3)
        formato = operacao.get("formato", "quadrado")

        elemento = criar_elemento_estruturante(tamanho, formato)

        if tipo == "erosao":
            img_saida = erosao(img_saida, elemento)

        elif tipo == "dilatacao":
            img_saida = dilatacao(img_saida, elemento)

        elif tipo == "abertura":
            img_saida = abertura(img_saida, elemento)

        elif tipo == "fechamento":
            img_saida = fechamento(img_saida, elemento)

        else:
            print("Operação morfológica desconhecida:", tipo)

    return img_saida
