"""Configurações gerais do jogo: tela, cores, posições, tempos e balanceamento.

Quase tudo que é "número mágico" do jogo fica aqui, para ficar fácil de ajustar.
"""
import os

# --- Pastas ---
PASTA_JOGO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_IMAGENS = os.path.join(PASTA_JOGO, 'assets', 'imagens')
PASTA_SONS = os.path.join(PASTA_JOGO, 'assets', 'sons')

# --- Tela ---
LARGURA_TELA = 1280
ALTURA_TELA = 720
TITULO = 'Pato Game'
TAMANHO_FONTE = 48

# --- Cores ---
VERMELHO = (234, 95, 112)
AZUL = (121, 161, 191)
AZUL_CLARO = (207, 228, 245)
VERDE = (114, 167, 139)
AZUL_TEMPO = (108, 137, 244)

# --- Torrada (área clicável) ---
TORRADA_RECT = (510, 201, 260, 242)  # x, y, largura, altura

# --- Barra de vida da torrada ---
BARRA_VIDA_POS = (518, 160)
BARRA_VIDA_LARGURA = 243
BARRA_VIDA_ALTURA = 20

# --- Botões circulares (posição do centro e raio) ---
BOTAO_AVANCO_NIVEL_POS = (1121, 127)
BOTAO_AVANCO_NIVEL_RAIO = 40
BOTAO_VOLTAR_NIVEL_POS = (1047, 79)
BOTAO_VOLTAR_NIVEL_RAIO = 20
BOTAO_LOJA_RAIO = 40

# --- Posições dos textos ---
TEXTO_VIDA_POS = (541, 115)
TEXTO_PATOCOINS_POS = (130, 45)
TEXTO_DPS_POS = (110, 145)
TEXTO_DANO_POS = (72, 235)
TEXTO_RECOMPENSA_POS = (610, 448)
TEXTO_TEMPO_BOSS_POS = (711, 114)
TEXTO_NIVEL_POS = (1100, 68)

# --- Tempos (em milissegundos) ---
DPS_INTERVALO = 800                 # de quanto em quanto tempo o DPS é aplicado
DANO_CLIQUE_INTERVALO_INICIAL = 2000  # intervalo inicial do clique automático (pato musculoso)
DANO_CLIQUE_INTERVALO_MINIMO = 200    # o intervalo não diminui abaixo disso
DANO_CLIQUE_REDUCAO = 50              # quanto o intervalo diminui a cada compra
TEMPO_LIMITE_BOSS = 10000

# --- Balanceamento ---
DANO_INICIAL = 1
DPS_BASE_INICIAL = 10
NIVEL_BOSS_A_CADA = 5

# --- Debug / trapaças ---
PATOCOINS_TRAPACA = 1000000000000  # quantidade ganha ao apertar P
MOSTRAR_POSICAO_CLIQUE = True      # imprime no terminal onde o mouse clicou (útil para posicionar coisas)
