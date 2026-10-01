"""Tabela de níveis: qual torrada aparece, quanta vida ela tem e quantas patocoins dá.

Cada linha é:  nivel: (imagem_da_torrada, vida, recompensa)
A imagem é o nome do arquivo em assets/imagens/torradas (sem o .png).
Todo nível múltiplo de 5 é um boss (com tempo limite).
"""

NIVEIS = {
    # Torrada nerd
    1: ('torradanerd', 10, 30),
    2: ('torradanerd', 25, 70),
    3: ('torradanerd', 30, 100),
    4: ('torradanerd', 40, 200),

    # Torrada feliz
    5: ('torradafeliz', 300, 1000),  # boss
    6: ('torradafeliz', 100, 500),
    7: ('torradafeliz', 100, 550),
    8: ('torradafeliz', 100, 575),
    9: ('torradafeliz', 100, 600),

    # Torrada virada (ao contrário)
    10: ('torradavirada', 500, 5000),  # boss
    11: ('torradavirada', 500, 6000),
    12: ('torradavirada', 500, 7000),
    13: ('torradavirada', 500, 8000),
    14: ('torradavirada', 500, 9000),

    # Torrada mofada
    15: ('torradamofada', 1000, 20000),  # boss
    16: ('torradamofada', 1000, 3000),
    17: ('torradamofada', 1000, 4000),
    18: ('torradamofada', 1000, 50000),
    19: ('torradamofada', 1000, 100000),

    # Torrada coquette
    20: ('torradacoquette', 4000, 400000),  # boss
    21: ('torradacoquette', 4000, 500000),
    22: ('torradacoquette', 4000, 600000),
    23: ('torradacoquette', 4000, 700000),
    24: ('torradacoquette', 4000, 800000),

    # Torrada interrogação
    25: ('torradainterrogacao', 40000, 1000000),  # boss
    26: ('torradainterrogacao', 40000, 4000000),
    27: ('torradainterrogacao', 40000, 8000000),
    28: ('torradainterrogacao', 40000, 10000000),
    29: ('torradainterrogacao', 40000, 20000000),

    # Torrada palhaço
    30: ('torradapalhaco', 70000, 50000000),  # boss
    31: ('torradapalhaco', 70000, 70000000),
    32: ('torradapalhaco', 70000, 90000000),
    33: ('torradapalhaco', 70000, 100000000),
    34: ('torradapalhaco', 70000, 200000000),

    # Torrada uwu
    35: ('torradauwu', 200000, 30000000),  # boss
    36: ('torradauwu', 200000, 40000000),
    37: ('torradauwu', 200000, 50000000),
    38: ('torradauwu', 200000, 60000000),
    39: ('torradauwu', 200000, 70000000),

    # Torradinha
    40: ('torradinha', 700000, 200000000),  # boss
    41: ('torradinha', 700000, 400000000),
    42: ('torradinha', 700000, 600000000),
    43: ('torradinha', 700000, 800000000),
    44: ('torradinha', 700000, 1000000000),

    # Torrada de chapéu
    45: ('torradadechapeu', 1000000, 10000000000),  # boss
    46: ('torradadechapeu', 1000000, 15000000000),
    47: ('torradadechapeu', 1000000, 20000000000),
    48: ('torradadechapeu', 1000000, 25000000000),
    49: ('torradadechapeu', 1000000, 30000000000),

    # "O que você está fazendo?"
    50: ('oquevoceestafazendo', 10000000, 30000000000),  # boss
    51: ('oquevoceestafazendo', 10000000, 60000000000),
    52: ('oquevoceestafazendo', 10000000, 90000000000),
    53: ('oquevoceestafazendo', 10000000, 100000000000),
    54: ('oquevoceestafazendo', 1000000000000, 10000000000000000000000),
}
