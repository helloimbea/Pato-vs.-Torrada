"""Level table: which toast appears, how much health it has and how many Duckcoins it gives.

Each line is:  level: (toast_image, health, reward)
The image is the file name in assets/images/toasts (without .png).
Every level that is a multiple of 5 is a boss (with a time limit).
"""

LEVELS = {
    # Nerd toast
    1: ('nerd_toast', 10, 30),
    2: ('nerd_toast', 25, 70),
    3: ('nerd_toast', 30, 100),
    4: ('nerd_toast', 40, 200),

    # Happy toast
    5: ('happy_toast', 300, 1000),  # boss
    6: ('happy_toast', 100, 500),
    7: ('happy_toast', 100, 550),
    8: ('happy_toast', 100, 575),
    9: ('happy_toast', 100, 600),

    # Upside-down toast
    10: ('upside_down_toast', 500, 5000),  # boss
    11: ('upside_down_toast', 500, 6000),
    12: ('upside_down_toast', 500, 7000),
    13: ('upside_down_toast', 500, 8000),
    14: ('upside_down_toast', 500, 9000),

    # Moldy toast
    15: ('moldy_toast', 1000, 20000),  # boss
    16: ('moldy_toast', 1000, 3000),
    17: ('moldy_toast', 1000, 4000),
    18: ('moldy_toast', 1000, 50000),
    19: ('moldy_toast', 1000, 100000),

    # Coquette toast
    20: ('coquette_toast', 4000, 400000),  # boss
    21: ('coquette_toast', 4000, 500000),
    22: ('coquette_toast', 4000, 600000),
    23: ('coquette_toast', 4000, 700000),
    24: ('coquette_toast', 4000, 800000),

    # Question mark toast
    25: ('question_mark_toast', 40000, 1000000),  # boss
    26: ('question_mark_toast', 40000, 4000000),
    27: ('question_mark_toast', 40000, 8000000),
    28: ('question_mark_toast', 40000, 10000000),
    29: ('question_mark_toast', 40000, 20000000),

    # Clown toast
    30: ('clown_toast', 70000, 50000000),  # boss
    31: ('clown_toast', 70000, 70000000),
    32: ('clown_toast', 70000, 90000000),
    33: ('clown_toast', 70000, 100000000),
    34: ('clown_toast', 70000, 200000000),

    # UwU toast
    35: ('uwu_toast', 200000, 30000000),  # boss
    36: ('uwu_toast', 200000, 40000000),
    37: ('uwu_toast', 200000, 50000000),
    38: ('uwu_toast', 200000, 60000000),
    39: ('uwu_toast', 200000, 70000000),

    # Tiny toast
    40: ('tiny_toast', 700000, 200000000),  # boss
    41: ('tiny_toast', 700000, 400000000),
    42: ('tiny_toast', 700000, 600000000),
    43: ('tiny_toast', 700000, 800000000),
    44: ('tiny_toast', 700000, 1000000000),

    # Hat toast
    45: ('hat_toast', 1000000, 10000000000),  # boss
    46: ('hat_toast', 1000000, 15000000000),
    47: ('hat_toast', 1000000, 20000000000),
    48: ('hat_toast', 1000000, 25000000000),
    49: ('hat_toast', 1000000, 30000000000),

    # "What are you doing?" toast
    50: ('what_are_you_doing_toast', 10000000, 30000000000),  # boss
    51: ('what_are_you_doing_toast', 10000000, 60000000000),
    52: ('what_are_you_doing_toast', 10000000, 90000000000),
    53: ('what_are_you_doing_toast', 10000000, 100000000000),
    54: ('what_are_you_doing_toast', 1000000000000, 10000000000000000000000),
}
