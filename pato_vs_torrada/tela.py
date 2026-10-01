"""Desenho de tudo que aparece na tela."""
import pygame

from . import config
from .loja import PATOS


def formatar_numero(num):
    """Deixa números grandes mais curtos: 1500 -> '1.5 K'."""
    if num >= 1000000000:
        return f'{round(num / 1000000000, 1)} BI'
    elif num >= 1000000:
        return f'{round(num / 1000000, 1)} MI'
    elif num >= 1000:
        return f'{round(num / 1000, 1)} K'
    else:
        return str(num)


def escrever(tela, fonte, texto, cor, posicao):
    tela.blit(fonte.render(texto, True, cor), posicao)


def desenhar(tela, fonte, recursos, estado, agora):
    # As imagens de patos, torradas e interface são do tamanho da tela,
    # por isso são todas desenhadas na posição (0, 0).
    tela.blit(recursos.mapa, (0, 0))

    # Barra de vida da torrada
    largura_barra = estado.vida * (config.BARRA_VIDA_LARGURA / estado.vida_max)
    barra = pygame.Rect(*config.BARRA_VIDA_POS, largura_barra, config.BARRA_VIDA_ALTURA)
    pygame.draw.rect(tela, config.VERMELHO, barra)

    # Patos comprados, torrada e pato inicial
    for nome in estado.patos_na_tela:
        tela.blit(recursos.patos[nome], (0, 0))
    if estado.torrada in recursos.torradas:
        tela.blit(recursos.torradas[estado.torrada], (0, 0))
    tela.blit(recursos.patos['patoinicial'], (0, 0))

    # Textos de status
    escrever(tela, fonte, str(round(estado.vida)), config.VERMELHO, config.TEXTO_VIDA_POS)
    escrever(tela, fonte, formatar_numero(estado.patocoins), config.AZUL_CLARO, config.TEXTO_PATOCOINS_POS)
    for pato in PATOS:
        escrever(tela, fonte, formatar_numero(estado.custos[pato.nome]), config.AZUL, pato.texto_custo_pos)
    escrever(tela, fonte, formatar_numero(estado.dps), config.AZUL_CLARO, config.TEXTO_DPS_POS)
    escrever(tela, fonte, formatar_numero(estado.dano), config.AZUL_CLARO, config.TEXTO_DANO_POS)
    escrever(tela, fonte, f'{estado.recompensa}', config.VERDE, config.TEXTO_RECOMPENSA_POS)

    if estado.mostrar_ponteiro:
        tela.blit(recursos.interface['ponteiro'], (0, 0))

    # Tempo do boss
    if estado.eh_boss():
        escrever(tela, fonte, f' {estado.tempo_restante_boss(agora)}', config.AZUL_TEMPO,
                 config.TEXTO_TEMPO_BOSS_POS)
        tela.blit(recursos.interface['caixinha'], (0, 0))

    # Botão de avanço de nível e nível atual
    imagem_nivel = 'nivelavanca' if estado.nivel_avanca else 'nivelbloq'
    tela.blit(recursos.interface[imagem_nivel], (0, 0))
    escrever(tela, fonte, f'{estado.nivel}', config.AZUL_CLARO, config.TEXTO_NIVEL_POS)

    # Patos que o jogador ainda não pode comprar ficam "bloqueados"
    for pato in PATOS:
        if estado.patocoins < estado.custos[pato.nome]:
            tela.blit(recursos.patos[pato.imagem_bloqueio], (0, 0))
    tela.blit(recursos.patos['bloqueiopatoburgues'], (0, 0))  # pato burguês: em breve
