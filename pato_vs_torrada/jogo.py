"""Loop principal do jogo e tratamento de cliques e teclas."""
import sys

import pygame

from . import config, loja
from .estado import EstadoJogo
from .recursos import Recursos
from .tela import desenhar


def clicou_no_circulo(posicao_mouse, centro, raio):
    return pygame.math.Vector2(centro).distance_to(posicao_mouse) < raio


def tratar_clique(evento, estado, recursos, torrada_rect):
    posicao = pygame.mouse.get_pos()
    if config.MOSTRAR_POSICAO_CLIQUE:
        print(f'Mouse clicked at: {posicao}')

    if clicou_no_circulo(posicao, config.BOTAO_AVANCO_NIVEL_POS, config.BOTAO_AVANCO_NIVEL_RAIO):
        estado.alternar_avanco_nivel()

    recursos.som_clique.play()

    if clicou_no_circulo(posicao, config.BOTAO_VOLTAR_NIVEL_POS, config.BOTAO_VOLTAR_NIVEL_RAIO):
        estado.voltar_nivel()

    if evento.button != 1:  # só o botão esquerdo ataca e compra
        return

    if torrada_rect.collidepoint(posicao):
        estado.causar_dano(estado.dano)

    for pato in loja.PATOS:
        if clicou_no_circulo(posicao, pato.botao_pos, config.BOTAO_LOJA_RAIO):
            loja.comprar(estado, pato)
            break


def main():
    pygame.init()
    tela = pygame.display.set_mode((config.LARGURA_TELA, config.ALTURA_TELA))
    pygame.display.set_caption(config.TITULO)
    pygame.mixer.init()

    recursos = Recursos()
    fonte = pygame.font.SysFont(None, config.TAMANHO_FONTE)
    torrada_rect = pygame.Rect(config.TORRADA_RECT)
    estado = EstadoJogo()
    botao_mouse_pressionado = False
    relogio = pygame.time.Clock()

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.MOUSEBUTTONDOWN and not botao_mouse_pressionado:
                botao_mouse_pressionado = True
                tratar_clique(evento, estado, recursos, torrada_rect)
            elif evento.type == pygame.MOUSEBUTTONUP:
                botao_mouse_pressionado = False

            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_p:
                estado.patocoins += config.PATOCOINS_TRAPACA

        agora = pygame.time.get_ticks()
        estado.atualizar(agora)
        desenhar(tela, fonte, recursos, estado, agora)
        pygame.display.update()
        relogio.tick(config.FPS)
