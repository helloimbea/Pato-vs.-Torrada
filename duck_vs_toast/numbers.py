"""Number formatting shared by the screen and the shop tooltips."""

NUMBER_SUFFIXES = ['', 'K', 'M', 'B', 'T', 'Qa', 'Qi', 'Sx', 'Sp', 'Oc', 'No', 'Dc']


def format_number(num):
    """Make numbers short and readable: 1500 -> '1.5 K', 12.5 -> '12.5', 2e12 -> '2 T'."""
    tier = 0
    while abs(num) >= 1000 and tier < len(NUMBER_SUFFIXES) - 1:
        num /= 1000
        tier += 1
    num = round(num, 1)
    if abs(num) >= 1000 and tier < len(NUMBER_SUFFIXES) - 1:  # e.g. 999.96 K rounds to 1000 K -> 1 M
        num = round(num / 1000, 1)
        tier += 1
    text = str(int(num)) if num == int(num) else str(num)
    suffix = NUMBER_SUFFIXES[tier]
    return f'{text} {suffix}' if suffix else text
