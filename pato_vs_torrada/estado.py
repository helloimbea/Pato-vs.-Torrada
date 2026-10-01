"""Estado do jogo: tudo que muda enquanto se joga (nível, vida, patocoins, ...)."""
import pygame

from . import config
from .loja import PATOS
from .niveis import NIVEIS


class EstadoJogo:
    def __init__(self):
        agora = pygame.time.get_ticks()

        # Progresso
        self.patocoins = 0
        self.nivel = 1
        self.nivel_avanca = True  # se False, o jogador fica "farmando" no mesmo nível

        # Torrada atual
        self.torrada = ''
        self.vida = 1
        self.vida_max = 1
        self.recompensa = 50
        self.inicio_boss = 0

        # Poder dos patos
        self.dano = config.DANO_INICIAL
        self.dps = 0
        self.dps_base = config.DPS_BASE_INICIAL
        self.dano_clique = 0  # clique automático do pato musculoso
        self.dano_clique_intervalo = config.DANO_CLIQUE_INTERVALO_INICIAL
        self.ultimo_dano_clique = agora
        self.ultimo_dps = agora

        # Loja
        self.custos = {pato.nome: pato.custo_inicial for pato in PATOS}
        self.patos_na_tela = []
        self.mostrar_ponteiro = False

        self.carregar_nivel()

    # --- Níveis ---

    def eh_boss(self):
        return self.nivel % config.NIVEL_BOSS_A_CADA == 0

    def carregar_nivel(self):
        """Coloca a torrada do nível atual na tela (com a vida cheia)."""
        dados = NIVEIS.get(self.nivel)
        if dados is None:
            return
        self.torrada, self.vida_max, self.recompensa = dados
        self.vida = self.vida_max
        if self.eh_boss():
            self.inicio_boss = pygame.time.get_ticks()

    def voltar_nivel(self):
        if self.nivel > 1:
            self.nivel -= 1
            self.carregar_nivel()

    def alternar_avanco_nivel(self):
        self.nivel_avanca = not self.nivel_avanca

    def tempo_restante_boss(self, agora):
        """Segundos que faltam para o boss recuperar a vida."""
        return max(0, (self.inicio_boss + config.TEMPO_LIMITE_BOSS - agora) // 1000)

    # --- Combate ---

    def causar_dano(self, quantidade):
        self.vida = max(self.vida - quantidade, 0)

    def atualizar(self, agora):
        """Chamado uma vez por frame: derrota da torrada, dano automático e tempo do boss."""
        if self.vida == 0:
            if self.nivel_avanca:
                self.nivel += 1
            self.patocoins += self.recompensa
            self.carregar_nivel()

        # Clique automático do pato musculoso
        if self.dano_clique > 0 and agora - self.ultimo_dano_clique >= self.dano_clique_intervalo:
            self.causar_dano(self.dano_clique)
            self.ultimo_dano_clique = agora

        # Dano por segundo
        if self.dps > 0 and agora - self.ultimo_dps >= config.DPS_INTERVALO:
            self.causar_dano(self.dps)
            self.ultimo_dps = agora

        # Se o tempo do boss acabar, ele recupera toda a vida
        if self.eh_boss() and agora - self.inicio_boss >= config.TEMPO_LIMITE_BOSS and self.vida > 0:
            self.vida = self.vida_max
            self.inicio_boss = pygame.time.get_ticks()
