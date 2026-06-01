import os
import time
from datetime import datetime
import numpy as np

from src.config import (
    PASTA_DATA,
    PASTA_RESULTADOS,
    PASTA_ANOTACOES,
    CONFIG_IMAGENS,
    FAIXAS_GRAO,
    FAIXAS_FUNDO
)

from src.utils import *
from src.roi import detectar_roi_circular_por_limiar
from src.filtros import aplicar_filtros
from src.frequencia import aplicar_filtros_frequencia
from src.pre_processamento import (
    converter_hsv,
    separar_canais_hsv,
    criar_mascara_objeto_por_faixas
)
from src.superpixels import (
    aplicar_superpixels_na_roi,
    segmentar_superpixels_por_otsu_hsv
)
from src.morfologia import aplicar_morfologia
from src.pos_processamento import aplicar_pos_processamento, contar_componentes
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
# COR_VERDE = "\033[92m"
# COR_AZUL = "\033[94m"
# COR_AMARELO = "\033[93m"
# COR_VERMELHO = "\033[91m"
# COR_RESET = "\033[0m"


# =========================
# FUNÇÕES AUXILIARES DE DEBUG
# =========================


# =========================
# REGISTROS ACUMULADOS
# =========================


# =========================
# EXECUÇÃO
# =========================
ID_EXECUCAO = "execucao_" + datetime.now().strftime("%Y%m%d_%H%M%S")

for config_imagem in CONFIG_IMAGENS:
    tempo_inicio_imagem = time.perf_counter()
    tempos_execucao = []

    nome_arquivo = config_imagem["nome_arquivo"]
    nome_base = config_imagem["nome_base"]
    area_minima_contagem = obter_area_minima_pos_processamento(config_imagem, valor_padrao=80)

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
    print("Área mínima de contagem:", area_minima_contagem)

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

    ajuste_roi = config_imagem.get("ajuste_roi", {})

    if ajuste_roi.get("usar", False):
        centro_x = ajuste_roi.get("centro_x", centro_x)
        centro_y = ajuste_roi.get("centro_y", centro_y)
        raio_roi = raio_roi + ajuste_roi.get("raio_extra", 0)

        img_roi, mascara_roi = criar_roi_circular_manual(
            img,
            centro_x,
            centro_y,
            raio_roi
        )

        print("ROI manual aplicada.")

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

    # A frequência é salva para análise, mas a segmentação por cor usa a ROI suavizada.
    img_hsv = converter_hsv(img_roi_suavizada)

    faixas_grao_imagem = config_imagem.get("faixas_grao", FAIXAS_GRAO)
    faixas_fundo_imagem = config_imagem.get("faixas_fundo", FAIXAS_FUNDO)

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

    mascara_grao_faixas, mascaras_objeto, mascaras_fundo = criar_mascara_objeto_por_faixas(
        img_hsv,
        faixas_grao_imagem,
        faixas_fundo_imagem
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
        os.path.join(pasta_saida_imagem, "mascara_grao_faixas_" + nome_base + ".png"),
        mascara_grao_faixas
    )

    mascara_grao, mascara_grao_h = aplicar_h_dominante_na_mascara(
        img_hsv,
        mascara_grao_faixas,
        mascara_roi,
        faixas_grao_imagem,
        config_imagem
    )

    if mascara_grao_h is not None:
        salvar_imagem(
            os.path.join(pasta_saida_imagem, "mascara_grao_h_dominante_" + nome_base + ".png"),
            mascara_grao_h
        )

    salvar_imagem(
        os.path.join(pasta_saida_imagem, "mascara_grao_inicial_" + nome_base + ".png"),
        mascara_grao
    )

    registrar_tempo(tempos_execucao, "Criação da máscara inicial do grão", inicio)

    imprimir_componentes_mascara(
        "Máscara por faixas HSV",
        mascara_grao_faixas,
        area_minima=area_minima_contagem
    )

    imprimir_componentes_mascara(
        "Máscara HSV + H dominante",
        mascara_grao,
        area_minima=area_minima_contagem
    )

    # =========================
    # SEGMENTAÇÃO POR SUPERPIXELS
    # =========================
    imprimir_etapa("Segmentação por superpixels")

    inicio = time.perf_counter()

    config_superpixels = config_imagem["superpixels"]

    labels_superpixels, imagem_labels, bordas_superpixels, mascara_grao_superpixel = aplicar_superpixels_na_roi(
        img_roi_suavizada,
        mascara_roi,
        mascara_grao,
        num_superpixels=config_superpixels["num_superpixels"],
        m=config_superpixels["m"],
        max_iter=config_superpixels["max_iter"],
        percentual_minimo=config_superpixels["percentual_minimo"],
        modo=config_superpixels["modo"]
    )

    # Otsu por superpixel fica salvo apenas para comparação visual.
    # Ele NÃO é usado como máscara final porque, nos testes, reduziu a contagem dos grãos.
    mascara_grao_otsu_superpixel, limiar_otsu_superpixel = segmentar_superpixels_por_otsu_hsv(
        labels_superpixels,
        img_hsv,
        mascara_roi,
        s_min=50,
        v_min=50,
        percentual_minimo=0.08
    )

    print("Limiar Otsu por superpixel no canal H:", limiar_otsu_superpixel)

    salvar_imagem(
        os.path.join(pasta_saida_imagem, "mascara_grao_otsu_superpixel_" + nome_base + ".png"),
        mascara_grao_otsu_superpixel
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

    imprimir_componentes_mascara(
        "Superpixel usando HSV/H manual",
        mascara_grao_superpixel,
        area_minima=area_minima_contagem
    )

    imprimir_componentes_mascara(
        "Superpixel usando Otsu automático",
        mascara_grao_otsu_superpixel,
        area_minima=area_minima_contagem
    )

    # =========================
    # MORFOLOGIA MATEMÁTICA
    # =========================
    imprimir_etapa("Morfologia matemática")

    inicio = time.perf_counter()

    # Usa a máscara refinada por superpixels, sem remover bordas.
    # Remover bordas de superpixel quebrou os grãos e aumentou demais a contagem.
    mascara_base_final = mascara_grao_superpixel

    mascara_grao_morfologia = aplicar_morfologia(
        mascara_base_final,
        config_imagem["morfologia"]
    )

    salvar_imagem(
        os.path.join(pasta_saida_imagem, "mascara_grao_morfologia_" + nome_base + ".png"),
        mascara_grao_morfologia
    )

    registrar_tempo(tempos_execucao, "Morfologia matemática", inicio)

    imprimir_componentes_mascara(
        "Depois da morfologia",
        mascara_grao_morfologia,
        area_minima=area_minima_contagem
    )

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

    imprimir_componentes_mascara(
        "Máscara final depois do pós-processamento",
        mascara_grao_final,
        area_minima=area_minima_contagem
    )

    # =========================
    # MÉTRICAS
    # =========================
    imprimir_etapa("Cálculo das métricas")

    inicio = time.perf_counter()

    if mascara_bbox is not None:
        metricas = salvar_metricas(
            pasta_saida_imagem,
            nome_base,
            mascara_grao_final,
            mascara_referencia=mascara_bbox,
            anotacoes=anotacoes,
            classe_interesse=config_imagem["classe_xml"],
            area_minima_contagem=area_minima_contagem
        )
    else:
        metricas = salvar_metricas(
            pasta_saida_imagem,
            nome_base,
            mascara_grao_final,
            mascara_referencia=None,
            anotacoes=None,
            classe_interesse=None,
            area_minima_contagem=area_minima_contagem
        )

    registrar_tempo(tempos_execucao, "Cálculo das métricas", inicio)

    print("Métricas salvas em:", metricas)

    salvar_registro_metricas(
        PASTA_RESULTADOS,
        nome_base,
        ID_EXECUCAO,
        metricas
    )

    salvar_registro_configuracao(
        PASTA_RESULTADOS,
        nome_base,
        ID_EXECUCAO,
        config_imagem
    )

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
