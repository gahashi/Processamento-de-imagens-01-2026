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
    {
        "nome_arquivo": "1027.jpg",
        "nome_base": "1027",
        "limiar_roi": 60,
        "margem_roi": 75,
        "classe_xml": None,

        "filtros": [],

        "frequencia": [
            {
                "tipo": "passa_baixa",
                "raio": 40,
                "canal": "v"
            }
        ],

        "superpixels": {
            "num_superpixels": 150,
            "m": 10,
            "max_iter": 2,
            "percentual_minimo": 0.25,
            "modo": "preencher"
        },

        "morfologia": [
            {
                "tipo": "abertura",
                "tamanho": 3,
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
                "area_minima": 300
            }
        ]
    },
    {
        "nome_arquivo": "1099.jpg",
        "nome_base": "1099",
        "limiar_roi": 60,
        "margem_roi": 75,
        "classe_xml": None,

        "filtros": [],

        "frequencia": [
            {
                "tipo": "passa_baixa",
                "raio": 40,
                "canal": "v"
            }
        ],

        "superpixels": {
            "num_superpixels": 80,
            "m": 10,
            "max_iter": 2,
            "percentual_minimo": 0.25,
            "modo": "preencher"
        },

        "morfologia": [
            {
                "tipo": "abertura",
                "tamanho": 3,
                "formato": "quadrado"
            }
        ],

        "pos_processamento": [
            {
                "tipo": "remover_componentes_pequenos",
                "area_minima": 300
            }
        ]
    },
    {
        "nome_arquivo": "1207.jpg",
        "nome_base": "1207",
        "limiar_roi": 60,
        "margem_roi": 75,
        "classe_xml": None,

        "filtros": [
            {
                "tipo": "mediana",
                "tamanho_kernel": 5
            }
        ],

        "frequencia": [
            {
                "tipo": "passa_baixa",
                "raio": 40,
                "canal": "v"
            }
        ],

        "superpixels": {
            "num_superpixels": 150,
            "m": 12,
            "max_iter": 2,
            "percentual_minimo": 0.30,
            "modo": "preencher"
        },

        "morfologia": [
            {
                "tipo": "abertura",
                "tamanho": 3,
                "formato": "quadrado"
            },
            {
                "tipo": "fechamento",
                "tamanho": 5,
                "formato": "quadrado"
            }
        ],

        "pos_processamento": [
            {
                "tipo": "remover_componentes_pequenos",
                "area_minima": 300
            }
        ]
    }
]