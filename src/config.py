# =========================
# CONFIGURAÇÕES DE PASTAS
# =========================
PASTA_DATA = "data"
PASTA_RESULTADOS = "resultados"
PASTA_ANOTACOES = "anotacoes"


# =========================
# FAIXAS HSV - OBJETO DE INTERESSE: GRÃO/SEMENTE
# =========================
FAIXAS_GRAO = [
{
        "nome": "grao_laranja_1099",
        "h_min": 18,
        "h_max": 35,
        "s_min": 120,
        "s_max": 255,
        "v_min": 120,
        "v_max": 255
    },
    {
        "nome": "grao_amarelo_laranja",
        "h_min": 8,
        "h_max": 26,
        "s_min": 80,
        "s_max": 255,
        "v_min": 100,
        "v_max": 255
    },
    {
        "nome": "mancha_escura_grao",
        "h_min": 5,
        "h_max": 15,
        "s_min": 150,
        "s_max": 255,
        "v_min": 20,
        "v_max": 100
    }
]


# =========================
# FAIXAS HSV - FUNDO PARA EXCLUSÃO/ANÁLISE
# =========================
FAIXAS_FUNDO = [
    {
        "nome": "fundo_azul_verde",
        "h_min": 78,
        "h_max": 105,
        "s_min": 180,
        "s_max": 255,
        "v_min": 40,
        "v_max": 170
    },
    {
        "nome": "fundo_escuro",
        "h_min": 0,
        "h_max": 55,
        "s_min": 0,
        "s_max": 70,
        "v_min": 0,
        "v_max": 120
    }
]


# =========================
# CONFIGURAÇÃO POR IMAGEM
# =========================
CONFIG_IMAGENS = [
    # {
    #     "nome_arquivo": "1027.jpg",
    #     "nome_base": "1027",
    #     "limiar_roi": 60,
    #     "margem_roi": 75,
    #     "classe_xml": None,
    #
    #     "faixas_grao": [
    #         {
    #             "nome": "grao_1027",
    #             "h_min": 12,
    #             "h_max": 30,
    #             "s_min": 80,
    #             "s_max": 255,
    #             "v_min": 100,
    #             "v_max": 255
    #         }
    #     ],
    #
    #     "faixas_fundo": [
    #         {
    #             "nome": "fundo_verde_ciano_1027",
    #             "h_min": 55,
    #             "h_max": 100,
    #             "s_min": 60,
    #             "s_max": 255,
    #             "v_min": 60,
    #             "v_max": 255
    #         }
    #     ],
    #
    #     "filtros": [],
    #
    #     "frequencia": [
    #         {
    #             "tipo": "passa_baixa",
    #             "raio": 40,
    #             "canal": "v"
    #         }
    #     ],
    #
    #     "superpixels": {
    #         "num_superpixels": 150,
    #         "m": 10,
    #         "max_iter": 2,
    #         "percentual_minimo": 0.25,
    #         "modo": "preencher"
    #     },
    #
    #     "morfologia": [
    #         {
    #             "tipo": "abertura",
    #             "tamanho": 3,
    #             "formato": "quadrado"
    #         },
    #         {
    #             "tipo": "fechamento",
    #             "tamanho": 3,
    #             "formato": "quadrado"
    #         }
    #     ],
    #
    #     "pos_processamento": [
    #         {
    #             "tipo": "remover_componentes_pequenos",
    #             "area_minima": 300
    #         }
    #     ]
    # },


    # ==========

{
    "nome_arquivo": "1027.jpg",
    "nome_base": "1027",
    "limiar_roi": 60,
    "margem_roi": 75,
    "classe_xml": None,

    "faixas_grao": [
        {
            "nome": "corpo_grao_laranja_1027",
            "h_min": 5,
            "h_max": 35,
            "s_min": 100,
            "s_max": 255,
            "v_min": 55,
            "v_max": 255
        }
    ],

    "faixas_fundo": None,

    "filtros": [],
    "frequencia": [],

    "h_dominante_min": 5,
    "h_dominante_max": 35,
    "h_dominante_s_min": 100,
    "h_dominante_v_min": 55,

    "superpixels": {
        "usar": False,
        "num_superpixels": 0,
        "m": 6,
        "max_iter": 0,
        "percentual_minimo": 0.05,
        "modo": "intersecao"
    },

    "morfologia": [
        {
            "tipo": "abertura",
            "tamanho": 7,
            "formato": "quadrado"
        },
        {
            "tipo": "fechamento",
            "tamanho": 3,
            "formato": "quadrado"
        }
    ],

    "pos_processamento": [
        {
            "tipo": "remover_componentes_pequenos",
            "area_minima": 120
        }
    ],
},

{
    "nome_arquivo": "1099.jpg",
    "nome_base": "1099",
    "limiar_roi": 0,
    "margem_roi": 0,
    "classe_xml": None,
    "ajuste_roi": {
        "usar": True,
        "centro_x": 959,
        "centro_y": 539,
        "raio_extra": 0
    },

    "faixas_grao": [
        {
            "nome": "corpo_grao_laranja_1099",
            "h_min": 5,
            "h_max": 35,
            "s_min": 100,
            "s_max": 255,
            "v_min": 55,
            "v_max": 255
        }
    ],

    "faixas_fundo": [
        {
            "nome": "fundo_azul_1099",
            "h_min": 78,
            "h_max": 125,
            "s_min": 40,
            "s_max": 255,
            "v_min": 25,
            "v_max": 255
        }
    ],

    "filtros": [],

    "frequencia": [],

    "h_dominante_min": 5,
    "h_dominante_max": 35,
    "h_dominante_s_min": 100,
    "h_dominante_v_min": 55,

    "superpixels": {
        "usar": False,
        "num_superpixels": 0,
        "m": 6,
        "max_iter": 0,
        "percentual_minimo": 0.05,
        "modo": "intersecao"
    },

    "morfologia": [
        {
            "tipo": "abertura",
            "tamanho": 7,
            "formato": "quadrado"
        },
        {
            "tipo": "fechamento",
            "tamanho": 3,
            "formato": "quadrado"
        }
    ],

    "pos_processamento": [
        {
            "tipo": "remover_componentes_pequenos",
            "area_minima": 120
        }
    ],

},

{
    "nome_arquivo": "1207.jpg",
    "nome_base": "1207",
    "limiar_roi": 60,
    "margem_roi": 75,
    "classe_xml": None,

    "faixas_grao": [
        {
            "nome": "corpo_grao_laranja_1207",
            "h_min": 5,
            "h_max": 35,
            "s_min": 100,
            "s_max": 255,
            "v_min": 55,
            "v_max": 255
        }
    ],

    "faixas_fundo": None,

    "filtros": [],
    "frequencia": [],

    "h_dominante_min": 5,
    "h_dominante_max": 35,
    "h_dominante_s_min": 100,
    "h_dominante_v_min": 55,

    "superpixels": {
        "usar": False,
        "num_superpixels": 0,
        "m": 6,
        "max_iter": 0,
        "percentual_minimo": 0.05,
        "modo": "intersecao"
    },

    "morfologia": [
        {
            "tipo": "abertura",
            "tamanho": 7,
            "formato": "quadrado"
        },
        {
            "tipo": "fechamento",
            "tamanho": 3,
            "formato": "quadrado"
        }
    ],

    "pos_processamento": [
        {
            "tipo": "remover_componentes_pequenos",
            "area_minima": 120
        },
        {
            "tipo": "separar_componentes_grandes_por_area",
            "area_media_grao": 4050,
            "area_minima": 120,
            "iteracoes": 12
        }
    ],
}
    # {
    #     "nome_arquivo": "1099.jpg",
    #     "nome_base": "1099",
    #     "limiar_roi": 60,
    #     "margem_roi": 75,
    #     "classe_xml": None,
    #
    #     "faixas_grao": [
    #         {
    #             "nome": "grao_laranja_1099",
    #             "h_min": 8,
    #             "h_max": 40,
    #             "s_min": 70,
    #             "s_max": 255,
    #             "v_min": 70,
    #             "v_max": 255
    #         }
    #     ],
    #
    #     "faixas_fundo": [
    #         {
    #             "nome": "fundo_azul_1099",
    #             "h_min": 85,
    #             "h_max": 115,
    #             "s_min": 80,
    #             "s_max": 255,
    #             "v_min": 40,
    #             "v_max": 255
    #         }
    #     ],
    #
    #     "filtros": [],
    #
    #     "frequencia": [
    #         {
    #             "tipo": "passa_baixa",
    #             "raio": 40,
    #             "canal": "v"
    #         }
    #     ],
    #
    #     "superpixels": {
    #         "num_superpixels": 80,
    #         "m": 15,
    #         "max_iter": 5,
    #         "percentual_minimo": 0.15,
    #         "modo": "preencher"
    #     },
    #
    #     "morfologia": [
    #         {
    #             "tipo": "erosao",
    #             "tamanho": 3,
    #             "formato": "cruz"
    #         },
    #         {
    #             "tipo": "abertura",
    #             "tamanho": 3,
    #             "formato": "cruz"
    #         }
    #     ],
    #
    #     "pos_processamento": [
    #         {
    #             "tipo": "remover_componentes_pequenos",
    #             "area_minima": 150
    #         }
    #     ]
    # },


    # =======================
    # {
    #     "nome_arquivo": "1207.jpg",
    #     "nome_base": "1207",
    #     "limiar_roi": 60,
    #     "margem_roi": 75,
    #     "classe_xml": None,
    #
    #     "faixas_grao": [
    #         {
    #             "nome": "grao_1207",
    #             "h_min": 10,
    #             "h_max": 30,
    #             "s_min": 70,
    #             "s_max": 255,
    #             "v_min": 90,
    #             "v_max": 255
    #         }
    #     ],
    #
    #     "faixas_fundo": [
    #         {
    #             "nome": "fundo_escuro_1207",
    #             "h_min": 0,
    #             "h_max": 179,
    #             "s_min": 0,
    #             "s_max": 90,
    #             "v_min": 0,
    #             "v_max": 80
    #         }
    #     ],
    #
    #     "filtros": [
    #         {
    #             "tipo": "mediana",
    #             "tamanho_kernel": 5
    #         }
    #     ],
    #
    #     "frequencia": [
    #         {
    #             "tipo": "passa_baixa",
    #             "raio": 40,
    #             "canal": "v"
    #         }
    #     ],
    #
    #     "superpixels": {
    #         "num_superpixels": 150,
    #         "m": 12,
    #         "max_iter": 2,
    #         "percentual_minimo": 0.30,
    #         "modo": "preencher"
    #     },
    #
    #     "morfologia": [
    #         {
    #             "tipo": "abertura",
    #             "tamanho": 3,
    #             "formato": "quadrado"
    #         },
    #         {
    #             "tipo": "fechamento",
    #             "tamanho": 5,
    #             "formato": "quadrado"
    #         }
    #     ],
    #
    #     "pos_processamento": [
    #         {
    #             "tipo": "remover_componentes_pequenos",
    #             "area_minima": 300
    #         }
    #     ]
    # }
]
