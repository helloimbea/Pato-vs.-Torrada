"""Carregamento de imagens e sons."""
import os

import pygame

from . import config


def carregar_imagem(categoria, nome):
    caminho = os.path.join(config.PASTA_IMAGENS, categoria, nome)
    return pygame.image.load(caminho).convert_alpha()


def carregar_pasta(categoria):
    """Carrega todas as imagens .png de uma pasta.

    Retorna um dicionário {nome_do_arquivo_sem_extensao: imagem}.
    Para adicionar uma imagem nova, basta colocar o arquivo na pasta certa.
    """
    pasta = os.path.join(config.PASTA_IMAGENS, categoria)
    imagens = {}
    for arquivo in sorted(os.listdir(pasta)):
        nome, extensao = os.path.splitext(arquivo)
        if extensao.lower() == '.png':
            imagens[nome] = carregar_imagem(categoria, arquivo)
    return imagens


class Recursos:
    """Guarda todas as imagens e sons do jogo.

    Precisa ser criado depois de pygame.display.set_mode().
    """

    def __init__(self):
        mapa = carregar_imagem('mapas', 'mapa1.png')
        self.mapa = pygame.transform.scale(mapa, (config.LARGURA_TELA, config.ALTURA_TELA))
        self.patos = carregar_pasta('patos')
        self.torradas = carregar_pasta('torradas')
        self.interface = carregar_pasta('interface')
        self.som_clique = pygame.mixer.Sound(os.path.join(config.PASTA_SONS, 'quack.wav'))
