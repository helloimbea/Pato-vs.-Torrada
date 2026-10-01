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
        if self.vida == 0:
            return
        self.vida = max(self.vida - quantidade, 0)
        if self.vida == 0:
            self.derrotar_torrada()

    def derrotar_torrada(self):
        """Dá a recompensa e passa para a próxima torrada (ou repete o nível)."""
        self.patocoins += self.recompensa
        if self.nivel_avanca and self.nivel + 1 in NIVEIS:
            self.nivel += 1
        self.carregar_nivel()

    @staticmethod
    def passou_intervalo(agora, ultimo, intervalo):
        """Diz se já deu o tempo do próximo golpe automático e calcula o novo "último".

        O novo "último" avança exatamente um intervalo, para que o atraso de cada
        quadro (até 1/FPS segundo) não se acumule e o dano por segundo fique certo.
        Se ficou muito para trás (ex.: o pato acabou de ser comprado), recomeça de agora.
        """
        if agora - ultimo < intervalo:
            return False, ultimo
        ultimo += intervalo
        if agora - ultimo >= intervalo:
            ultimo = agora
        return True, ultimo

    def atualizar(self, agora):
        """Chamado uma vez por quadro: dano automático e tempo do boss."""
        # Clique automático do pato musculoso
        if self.dano_clique > 0:
            bateu, self.ultimo_dano_clique = self.passou_intervalo(
                agora, self.ultimo_dano_clique, self.dano_clique_intervalo)
            if bateu:
                self.causar_dano(self.dano_clique)

        # Dano por segundo
        if self.dps > 0:
            bateu, self.ultimo_dps = self.passou_intervalo(agora, self.ultimo_dps, config.DPS_INTERVALO)
            if bateu:
                self.causar_dano(self.dps)

        # Se o tempo do boss acabar, ele recupera toda a vida
        if self.eh_boss() and agora - self.inicio_boss >= config.TEMPO_LIMITE_BOSS and self.vida > 0:
            self.vida = self.vida_max
            self.inicio_boss = agora
