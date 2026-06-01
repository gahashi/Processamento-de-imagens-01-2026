import os
import time
from datetime import datetime

from src.config import (
    PASTA_DATA,
    PASTA_RESULTADOS,
    PASTA_ANOTACOES,
    CONFIG_IMAGENS,
    FAIXAS_GRAO,
    FAIXAS_FUNDO
)

from src.utils import carregar_imagem, mostrar_imagem, salvar_imagem
from src.roi import detectar_roi_circular_por_limiar
from src.filtros import aplicar_filtros
from src.frequencia import aplicar_filtros_frequencia
from src.pre_processamento import (
    converter_hsv,
    separar_canais_hsv,
    criar_mascara_objeto_por_faixas
)
from src.superpixels import aplicar_superpixels_na_roi
from src.morfologia import aplicar_morfologia
from src.pos_processamento import aplicar_pos_processamento
from src.metricas import salvar_metricas
from src.anotacoes import (
    ler_anotacoes_xml,
    contar_anotacoes,
    criar_mascara_bbox,
    desenhar_bounding_boxes
)


# =========================
# CORES DO TERMINAL
# =========================
COR_VERDE = "\033[92m"
COR_AZUL = "\033[94m"
COR_AMARELO = "\033[93m"
COR_VERMELHO = "\033[91m"
COR_RESET = "\033[0m"


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


def salvar_tempos_execucao(pasta_resultados, nome_base, id_execucao, tempos, tempo_total):
    """
    Salva o tempo de execução na pasta raiz da imagem.

    Gera dois arquivos:
    - registros_tempo_XXXX.txt
    - registros_tempo_XXXX.csv

    O CSV pode ser aberto no Excel.
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

    # =========================
    # SALVA TXT
    # =========================
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

    # =========================
    # SALVA CSV
    # =========================
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

# =========================
# EXECUÇÃO
# =========================
ID_EXECUCAO = "execucao_" + datetime.now().strftime("%Y%m%d_%H%M%S")


for config_imagem in CONFIG_IMAGENS:
    tempo_inicio_imagem = time.perf_counter()
    tempos_execucao = []

    nome_arquivo = config_imagem["nome_arquivo"]
    nome_base = config_imagem["nome_base"]

    imprimir_titulo("PROCESSANDO IMAGEM " + nome_base)

    # =========================
    # PASTA DE SAÍDA
    # =========================
    pasta_saida_imagem = os.path.join(
        PASTA_RESULTADOS,
        nome_base,
        ID_EXECUCAO
    )

    os.makedirs(pasta_saida_imagem, exist_ok=True)

    print("Arquivo:", nome_arquivo)
    print("Resultados:", pasta_saida_imagem)

    # =========================
    # LEITURA DA IMAGEM
    # =========================
    imprimir_etapa("Leitura da imagem")

    inicio = time.perf_counter()

    caminho_img = os.path.join(PASTA_DATA, nome_arquivo)
    img = carregar_imagem(caminho_img)

    registrar_tempo(tempos_execucao, "Leitura da imagem", inicio)

    print("Dimensões:", img.shape)

    # =========================
    # ANOTAÇÕES XML
    # =========================
    imprimir_etapa("Leitura das anotações XML")

    inicio = time.perf_counter()

    caminho_xml = os.path.join(PASTA_ANOTACOES, nome_base + ".xml")

    anotacoes = []
    mascara_bbox = None

    if os.path.exists(caminho_xml):
        anotacoes = ler_anotacoes_xml(caminho_xml)

        contagem = contar_anotacoes(anotacoes)
        print("Anotações encontradas:", contagem)

        img_bbox = desenhar_bounding_boxes(img, anotacoes)

        salvar_imagem(
            os.path.join(pasta_saida_imagem, "bbox_" + nome_base + ".png"),
            img_bbox
        )

        altura, largura = img.shape[:2]

        mascara_bbox = criar_mascara_bbox(
            altura,
            largura,
            anotacoes,
            classe_interesse=config_imagem["classe_xml"]
        )

        salvar_imagem(
            os.path.join(pasta_saida_imagem, "mascara_bbox_" + nome_base + ".png"),
            mascara_bbox
        )

    else:
        print(COR_VERMELHO + "XML não encontrado: " + caminho_xml + COR_RESET)

    registrar_tempo(tempos_execucao, "Leitura das anotações XML", inicio)

    # =========================
    # ROI CIRCULAR
    # =========================
    imprimir_etapa("Detecção da ROI circular")

    inicio = time.perf_counter()

    img_roi, mascara_roi, centro_x, centro_y, raio_roi = detectar_roi_circular_por_limiar(
        img,
        limiar=config_imagem["limiar_roi"],
        margem=config_imagem["margem_roi"]
    )

    salvar_imagem(
        os.path.join(pasta_saida_imagem, "roi_" + nome_base + ".png"),
        img_roi
    )

    salvar_imagem(
        os.path.join(pasta_saida_imagem, "mascara_roi_" + nome_base + ".png"),
        mascara_roi
    )

    registrar_tempo(tempos_execucao, "Detecção da ROI circular", inicio)

    print("Centro ROI:", centro_x, centro_y)
    print("Raio ROI:", raio_roi)

    # =========================
    # FILTROS ESPACIAIS
    # =========================
    imprimir_etapa("Filtros espaciais")

    inicio = time.perf_counter()

    img_roi_suavizada = aplicar_filtros(
        img_roi,
        config_imagem["filtros"]
    )

    salvar_imagem(
        os.path.join(pasta_saida_imagem, "roi_suavizada_" + nome_base + ".png"),
        img_roi_suavizada
    )

    registrar_tempo(tempos_execucao, "Filtros espaciais", inicio)

    # =========================
    # FILTRAGEM NO DOMÍNIO DA FREQUÊNCIA
    # =========================
    imprimir_etapa("Filtragem no domínio da frequência")

    inicio = time.perf_counter()

    img_frequencia, resultados_frequencia = aplicar_filtros_frequencia(
        img_roi_suavizada,
        config_imagem["frequencia"]
    )

    salvar_imagem(
        os.path.join(pasta_saida_imagem, "roi_frequencia_" + nome_base + ".png"),
        img_frequencia
    )

    for nome_resultado, img_resultado in resultados_frequencia.items():
        salvar_imagem(
            os.path.join(pasta_saida_imagem, nome_resultado + "_" + nome_base + ".png"),
            img_resultado
        )

    registrar_tempo(tempos_execucao, "Filtragem no domínio da frequência", inicio)

    # =========================
    # CONVERSÃO HSV
    # =========================
    imprimir_etapa("Conversão HSV e separação dos canais")

    inicio = time.perf_counter()

    img_hsv = converter_hsv(img_frequencia)

    h, s, v = separar_canais_hsv(img_hsv)

    salvar_imagem(
        os.path.join(pasta_saida_imagem, "canal_h_" + nome_base + ".png"),
        h
    )

    salvar_imagem(
        os.path.join(pasta_saida_imagem, "canal_s_" + nome_base + ".png"),
        s
    )

    salvar_imagem(
        os.path.join(pasta_saida_imagem, "canal_v_" + nome_base + ".png"),
        v
    )

    registrar_tempo(tempos_execucao, "Conversão HSV e separação dos canais", inicio)

    # =========================
    # MÁSCARA INICIAL DO GRÃO
    # =========================
    imprimir_etapa("Criação da máscara inicial do grão")

    inicio = time.perf_counter()

    mascara_grao, mascaras_objeto, mascaras_fundo = criar_mascara_objeto_por_faixas(
        img_hsv,
        FAIXAS_GRAO,
        FAIXAS_FUNDO
    )

    for nome_mascara, mascara in mascaras_objeto.items():
        salvar_imagem(
            os.path.join(
                pasta_saida_imagem,
                "mascara_" + nome_mascara + "_" + nome_base + ".png"
            ),
            mascara
        )

    for nome_mascara, mascara in mascaras_fundo.items():
        salvar_imagem(
            os.path.join(
                pasta_saida_imagem,
                "mascara_" + nome_mascara + "_" + nome_base + ".png"
            ),
            mascara
        )

    salvar_imagem(
        os.path.join(pasta_saida_imagem, "mascara_grao_inicial_" + nome_base + ".png"),
        mascara_grao
    )

    registrar_tempo(tempos_execucao, "Criação da máscara inicial do grão", inicio)

    # =========================
    # SEGMENTAÇÃO POR SUPERPIXELS
    # =========================
    imprimir_etapa("Segmentação por superpixels")

    inicio = time.perf_counter()

    config_superpixels = config_imagem["superpixels"]

    labels_superpixels, imagem_labels, bordas_superpixels, mascara_grao_superpixel = aplicar_superpixels_na_roi(
        img_frequencia,
        mascara_roi,
        mascara_grao,
        num_superpixels=config_superpixels["num_superpixels"],
        m=config_superpixels["m"],
        max_iter=config_superpixels["max_iter"],
        percentual_minimo=config_superpixels["percentual_minimo"],
        modo=config_superpixels["modo"]
    )

    salvar_imagem(
        os.path.join(pasta_saida_imagem, "superpixels_labels_" + nome_base + ".png"),
        imagem_labels
    )

    salvar_imagem(
        os.path.join(pasta_saida_imagem, "superpixels_bordas_" + nome_base + ".png"),
        bordas_superpixels
    )

    salvar_imagem(
        os.path.join(pasta_saida_imagem, "mascara_grao_superpixel_" + nome_base + ".png"),
        mascara_grao_superpixel
    )

    registrar_tempo(tempos_execucao, "Segmentação por superpixels", inicio)

    # =========================
    # MORFOLOGIA MATEMÁTICA
    # =========================
    imprimir_etapa("Morfologia matemática")

    inicio = time.perf_counter()

    mascara_grao_morfologia = aplicar_morfologia(
        mascara_grao_superpixel,
        config_imagem["morfologia"]
    )

    salvar_imagem(
        os.path.join(pasta_saida_imagem, "mascara_grao_morfologia_" + nome_base + ".png"),
        mascara_grao_morfologia
    )

    registrar_tempo(tempos_execucao, "Morfologia matemática", inicio)

    # =========================
    # PÓS-PROCESSAMENTO
    # =========================
    imprimir_etapa("Pós-processamento")

    inicio = time.perf_counter()

    mascara_grao_final = aplicar_pos_processamento(
        mascara_grao_morfologia,
        config_imagem["pos_processamento"]
    )

    salvar_imagem(
        os.path.join(pasta_saida_imagem, "mascara_grao_final_" + nome_base + ".png"),
        mascara_grao_final
    )

    registrar_tempo(tempos_execucao, "Pós-processamento", inicio)

    # =========================
    # MÉTRICAS
    # =========================
    imprimir_etapa("Cálculo das métricas")

    inicio = time.perf_counter()

    if mascara_bbox is not None:
        caminho_metricas = salvar_metricas(
            pasta_saida_imagem,
            nome_base,
            mascara_grao_final,
            mascara_referencia=mascara_bbox,
            anotacoes=anotacoes,
            classe_interesse=config_imagem["classe_xml"],
            area_minima_contagem=300
        )
    else:
        caminho_metricas = salvar_metricas(
            pasta_saida_imagem,
            nome_base,
            mascara_grao_final,
            mascara_referencia=None,
            anotacoes=None,
            classe_interesse=None,
            area_minima_contagem=300
        )

    registrar_tempo(tempos_execucao, "Cálculo das métricas", inicio)

    print("Métricas salvas em:", caminho_metricas)

    # =========================
    # TEMPO TOTAL DA IMAGEM
    # =========================
    tempo_total_imagem = time.perf_counter() - tempo_inicio_imagem

    caminho_tempos_txt, caminho_tempos_csv = salvar_tempos_execucao(
        PASTA_RESULTADOS,
        nome_base,
        ID_EXECUCAO,
        tempos_execucao,
        tempo_total_imagem
    )

    imprimir_linha()
    print(COR_VERDE + "Imagem " + nome_base + " finalizada em " + str(round(tempo_total_imagem, 4)) + "s" + COR_RESET)
    print("Registro TXT:", caminho_tempos_txt)
    print("Registro CSV:", caminho_tempos_csv)
    imprimir_linha()

    # =========================
    # VISUALIZAÇÃO
    # =========================
    # Durante os testes em lote, recomendo deixar comentado.
    # mostrar_imagem("Imagem com ROI", img_roi)
    # mostrar_imagem("Mascara Grao Inicial", mascara_grao)
    # mostrar_imagem("Mascara Grao Superpixel", mascara_grao_superpixel)
    # mostrar_imagem("Mascara Grao Final", mascara_grao_final)