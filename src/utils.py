import os
import cv2
import time
import numpy as np
from src.pos_processamento import  contar_componentes


COR_VERDE = "\033[92m"
COR_AZUL = "\033[94m"
COR_AMARELO = "\033[93m"
COR_VERMELHO = "\033[91m"
COR_RESET = "\033[0m"


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


def criar_roi_circular_manual(img, centro_x, centro_y, raio):
    """
    Cria uma ROI circular manual usando centro e raio definidos.
    Pixels fora do círculo ficam pretos.
    """

    altura, largura = img.shape[:2]

    y_indices, x_indices = np.ogrid[:altura, :largura]

    distancia = (x_indices - centro_x) ** 2 + (y_indices - centro_y) ** 2
    mascara_roi = np.zeros((altura, largura), dtype=np.uint8)
    mascara_roi[distancia <= raio ** 2] = 255

    img_roi = img.copy()
    img_roi[mascara_roi == 0] = 0

    return img_roi, mascara_roi

def imprimir_linha():
    print(COR_AZUL + "-" * 70 + COR_RESET)


def imprimir_titulo(texto):
    print()
    imprimir_linha()
    print(COR_VERDE + texto + COR_RESET)
    imprimir_linha()


def imprimir_etapa(texto):
    print(COR_AMARELO + "[ETAPA] " + texto + COR_RESET)


def imprimir_tempo(nome_etapa, tempo_segundos):
    print(COR_VERDE + "[OK] " + nome_etapa + " finalizada em " + str(round(tempo_segundos, 4)) + "s" + COR_RESET)


def registrar_tempo(lista_tempos, nome_etapa, inicio):
    tempo = time.perf_counter() - inicio

    lista_tempos.append({
        "etapa": nome_etapa,
        "tempo_segundos": tempo
    })

    imprimir_tempo(nome_etapa, tempo)

    return tempo


def imprimir_componentes_mascara(nome_etapa, mascara, area_minima=80):
    """
    Imprime quantos componentes conectados existem em uma máscara.
    Serve para descobrir em qual etapa os grãos estão sendo perdidos ou quebrados.
    """

    total = contar_componentes(
        mascara,
        area_minima=area_minima
    )

    print(
        COR_AMARELO +
        "[DEBUG CONTAGEM] " +
        nome_etapa +
        ": " +
        str(total) +
        " componentes" +
        " | área mínima: " +
        str(area_minima) +
        COR_RESET
    )

    return total


def obter_area_minima_pos_processamento(config_imagem, valor_padrao=80):
    """
    Pega a área mínima usada no pós-processamento para usar também no debug e nas métricas.
    Assim a contagem do debug e a contagem da métrica ficam coerentes.
    """

    lista_pos = config_imagem.get("pos_processamento", [])

    for operacao in lista_pos:
        if operacao.get("tipo") == "remover_componentes_pequenos":
            return int(operacao.get("area_minima", valor_padrao))

    return valor_padrao


def valor_csv(valor):
    """
    Converte valores para escrita em CSV.
    """

    if valor is None:
        return ""

    return str(valor)


# =========================
# FUNÇÕES AUXILIARES DE MÁSCARA
# =========================
def criar_mascara_h_dominante(img_hsv, h_min, h_max, s_min=50, v_min=50, mascara_roi=None):
    """
    Cria uma máscara usando principalmente o canal H.
    Mantém S e V apenas como proteção para não pegar fundo muito escuro/cinza.
    """

    h = img_hsv[:, :, 0]
    s = img_hsv[:, :, 1]
    v = img_hsv[:, :, 2]

    if h_min <= h_max:
        cond_h = (h >= h_min) & (h <= h_max)
    else:
        cond_h = (h >= h_min) | (h <= h_max)

    cond = cond_h & (s >= s_min) & (v >= v_min)

    if mascara_roi is not None:
        cond = cond & (mascara_roi > 0)

    mascara = np.where(cond, 255, 0).astype(np.uint8)

    return mascara


def combinar_mascaras_numpy(mascara_a, mascara_b):
    """
    Combina duas máscaras binárias.
    Se uma das duas tiver pixel branco, o resultado fica branco.
    """

    return np.where(
        (mascara_a > 0) | (mascara_b > 0),
        255,
        0
    ).astype(np.uint8)


def aplicar_h_dominante_na_mascara(img_hsv, mascara_grao, mascara_roi, faixas_grao_imagem, config_imagem):
    """
    Complementa a máscara inicial com uma máscara baseada no canal H.

    Motivo:
    Nos testes da imagem 1099, o canal H identificou bem os grãos.
    A máscara por H precisa ser aplicada ANTES dos superpixels, para que o SLIC refine
    uma máscara inicial melhor.
    """

    if len(faixas_grao_imagem) == 0:
        return mascara_grao, None

    faixa_principal = faixas_grao_imagem[0]

    h_min = config_imagem.get("h_dominante_min", faixa_principal["h_min"])
    h_max = config_imagem.get("h_dominante_max", faixa_principal["h_max"])

    # Mantém S e V um pouco mais permissivos que a faixa principal.
    s_min = config_imagem.get("h_dominante_s_min", min(50, faixa_principal.get("s_min", 50)))
    v_min = config_imagem.get("h_dominante_v_min", min(50, faixa_principal.get("v_min", 50)))

    mascara_grao_h = criar_mascara_h_dominante(
        img_hsv,
        h_min=h_min,
        h_max=h_max,
        s_min=s_min,
        v_min=v_min,
        mascara_roi=mascara_roi
    )

    mascara_combinada = combinar_mascaras_numpy(
        mascara_grao,
        mascara_grao_h
    )

    return mascara_combinada, mascara_grao_h

def salvar_registro_metricas(
        pasta_resultados,
        nome_base,
        id_execucao,
        metricas
):
    """
    Salva um registro acumulado das métricas na pasta raiz da imagem.
    """

    pasta_raiz_imagem = os.path.join(
        pasta_resultados,
        nome_base
    )

    os.makedirs(pasta_raiz_imagem, exist_ok=True)

    caminho_csv = os.path.join(
        pasta_raiz_imagem,
        "registros_metricas_" + nome_base + ".csv"
    )

    arquivo_existe = os.path.exists(caminho_csv)

    with open(caminho_csv, "a", encoding="utf-8") as arquivo:
        if not arquivo_existe:
            arquivo.write(
                "imagem;execucao;total_detectado;total_anotado;"
                "erro_absoluto;erro_percentual;iou;dice\n"
            )

        arquivo.write(
            nome_base + ";" +
            id_execucao + ";" +
            valor_csv(metricas["total_detectado"]) + ";" +
            valor_csv(metricas["total_anotado"]) + ";" +
            valor_csv(metricas["erro_absoluto"]) + ";" +
            valor_csv(
                round(metricas["erro_percentual"], 4) if metricas["erro_percentual"] is not None else None) + ";" +
            valor_csv(round(metricas["iou"], 4) if metricas["iou"] is not None else None) + ";" +
            valor_csv(round(metricas["dice"], 4) if metricas["dice"] is not None else None) + "\n"
        )

    return caminho_csv


def salvar_registro_configuracao(
        pasta_resultados,
        nome_base,
        id_execucao,
        config_imagem
):
    """
    Salva um registro acumulado com as configurações usadas em cada execução.
    """

    pasta_raiz_imagem = os.path.join(
        pasta_resultados,
        nome_base
    )

    os.makedirs(pasta_raiz_imagem, exist_ok=True)

    caminho_csv = os.path.join(
        pasta_raiz_imagem,
        "registros_config_" + nome_base + ".csv"
    )

    arquivo_existe = os.path.exists(caminho_csv)

    superpixels = config_imagem["superpixels"]

    if len(config_imagem["frequencia"]) > 0:
        frequencia = config_imagem["frequencia"][0]
    else:
        frequencia = {
            "tipo": "",
            "raio": "",
            "canal": ""
        }

    if len(config_imagem["pos_processamento"]) > 0:
        pos = config_imagem["pos_processamento"][0]
    else:
        pos = {
            "area_minima": ""
        }

    with open(caminho_csv, "a", encoding="utf-8") as arquivo:
        if not arquivo_existe:
            arquivo.write(
                "imagem;execucao;limiar_roi;margem_roi;classe_xml;"
                "freq_tipo;freq_raio;freq_canal;"
                "num_superpixels;m;max_iter;percentual_minimo;modo;"
                "area_minima_pos_processamento\n"
            )

        arquivo.write(
            nome_base + ";" +
            id_execucao + ";" +
            valor_csv(config_imagem["limiar_roi"]) + ";" +
            valor_csv(config_imagem["margem_roi"]) + ";" +
            valor_csv(config_imagem["classe_xml"]) + ";" +
            valor_csv(frequencia.get("tipo", "")) + ";" +
            valor_csv(frequencia.get("raio", "")) + ";" +
            valor_csv(frequencia.get("canal", "")) + ";" +
            valor_csv(superpixels["num_superpixels"]) + ";" +
            valor_csv(superpixels["m"]) + ";" +
            valor_csv(superpixels["max_iter"]) + ";" +
            valor_csv(superpixels["percentual_minimo"]) + ";" +
            valor_csv(superpixels["modo"]) + ";" +
            valor_csv(pos.get("area_minima", "")) + "\n"
        )

    return caminho_csv


def salvar_tempos_execucao(pasta_resultados, nome_base, id_execucao, tempos, tempo_total):
    """
    Salva o tempo de execução na pasta raiz da imagem.

    Gera dois arquivos:
    - registros_tempo_XXXX.txt
    - registros_tempo_XXXX.csv
    """

    pasta_raiz_imagem = os.path.join(
        pasta_resultados,
        nome_base
    )

    os.makedirs(pasta_raiz_imagem, exist_ok=True)

    caminho_txt = os.path.join(
        pasta_raiz_imagem,
        "registros_tempo_" + nome_base + ".txt"
    )

    caminho_csv = os.path.join(
        pasta_raiz_imagem,
        "registros_tempo_" + nome_base + ".csv"
    )

    with open(caminho_txt, "a", encoding="utf-8") as arquivo:
        arquivo.write("=" * 70 + "\n")
        arquivo.write("Imagem: " + nome_base + "\n")
        arquivo.write("Execução: " + id_execucao + "\n")
        arquivo.write("Tempo total: " + str(round(tempo_total, 4)) + "s\n")
        arquivo.write("\n")
        arquivo.write("Tempos por etapa:\n")

        for item in tempos:
            arquivo.write(
                "- " + item["etapa"] + ": " + str(round(item["tempo_segundos"], 4)) + "s\n"
            )

        arquivo.write("\n")

    arquivo_existe = os.path.exists(caminho_csv)

    with open(caminho_csv, "a", encoding="utf-8") as arquivo:
        if not arquivo_existe:
            arquivo.write("imagem;execucao;etapa;tempo_segundos\n")

        arquivo.write(
            nome_base + ";" +
            id_execucao + ";" +
            "TOTAL" + ";" +
            str(round(tempo_total, 4)) + "\n"
        )

        for item in tempos:
            arquivo.write(
                nome_base + ";" +
                id_execucao + ";" +
                item["etapa"] + ";" +
                str(round(item["tempo_segundos"], 4)) + "\n"
            )

    return caminho_txt, caminho_csv
