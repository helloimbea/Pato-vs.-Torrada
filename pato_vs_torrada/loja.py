"""Loja de patos: o que cada pato custa e o que ele faz quando é comprado.

Para criar um pato novo:
  1. coloque a imagem dele (e a versão "bloqueio") em assets/imagens/patos;
  2. escreva uma função de efeito (como as de baixo);
  3. adicione um Pato na lista PATOS.
"""
import math
from dataclasses import dataclass
from typing import Callable

from . import config


@dataclass
class Pato:
    nome: str                  # nome da imagem em assets/imagens/patos
    custo_inicial: int
    multiplicador_custo: float  # o custo é multiplicado por isso a cada compra
    botao_pos: tuple           # centro do botão de compra
    texto_custo_pos: tuple     # onde o custo é escrito
    efeito: Callable           # função que recebe o estado do jogo

    @property
    def imagem_bloqueio(self):
        return 'bloqueio' + self.nome


# --- Efeitos de cada pato ---

def efeito_pato_siames(estado):
    """Adiciona DPS."""
    estado.dps += estado.dps_base


def efeito_pato_dobrado(estado):
    """Dobra o dano do clique."""
    estado.dano *= 2


def efeito_pato_musculoso(estado):
    """Clica sozinho, cada vez mais rápido."""
    estado.dano_clique = estado.dano
    if estado.dano_clique_intervalo > config.DANO_CLIQUE_INTERVALO_MINIMO:
        estado.dano_clique_intervalo -= config.DANO_CLIQUE_REDUCAO
    estado.mostrar_ponteiro = True


def efeito_pato_realista(estado):
    """Dobra o DPS total."""
    estado.dps *= 2
    estado.dps_base *= 2


PATOS = [
    Pato('patosiames', 200, 1.5, (157, 605), (119, 675), efeito_pato_siames),
    Pato('patodobrado', 5000, 3, (399, 603), (381, 675), efeito_pato_dobrado),
    Pato('patomusculoso', 50000, 2, (641, 603), (616, 675), efeito_pato_musculoso),
    Pato('patorealista', 200000, 4, (883, 603), (863, 675), efeito_pato_realista),
    # Pato burguês (em breve) ficaria no botão (1125, 603)
]


def comprar(estado, pato):
    custo = estado.custos[pato.nome]
    if estado.patocoins < custo:
        return
    if pato.nome not in estado.patos_na_tela:
        estado.patos_na_tela.append(pato.nome)
    estado.patocoins -= custo
    pato.efeito(estado)
    estado.custos[pato.nome] = math.floor(custo * pato.multiplicador_custo)
