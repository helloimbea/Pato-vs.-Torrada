"""Languages: every text the code writes on screen, in English and in Portuguese.

To change a text, edit it here. To add a text, add the same key to both languages and
use t('key') in the code. Texts with {name} get values filled in: t('bought', count=3).

Drawn text (toast names, shop titles, "LVL") is part of the drawings. The drawings as they
are now are the Portuguese ones; an English version of a drawing is the same file name
ending in "_en" (for example nerd_toast_en.png or map1_en.png). Until it exists, the
Portuguese drawing is shown in English too (see assets.localized).
"""
import locale

LANGUAGES = ('en', 'pt')

TEXTS = {
    'en': {
        'title': 'Duck vs. Toast',
        'click_to_play': 'Click anywhere to play',
        'welcome_back': 'Welcome back! You were away for {time}.',
        'ducks_earned': 'Your ducks earned {amount} Duckcoins.',
        'paused': 'Paused',
        'press_to_continue': 'Press Esc or click to continue',
        'victory': 'You beat every toast!',
        'toasts_are_back': "But the toasts are back... and stronger.",
        'keep_playing': 'Click to keep playing',
        'bought': 'Bought: {count}',
        'siamese_duck': 'Siamese Duck',
        'siamese_duck_effect': 'Adds {dps} damage per second.',
        'double_duck': 'Double Duck',
        'double_duck_effect': 'Doubles your click damage ({now} -> {next}).',
        'muscular_duck': 'Muscular Duck',
        'muscular_duck_effect': 'Clicks the toast for you every {seconds} s, with your click damage.',
        'realistic_duck': 'Realistic Duck',
        'realistic_duck_effect': 'Doubles all damage per second ({now} -> {next}).',
        'bourgeois_duck': 'Bourgeois Duck',
        'bourgeois_duck_effect': 'For {minutes} min: x{damage} damage and x{coins} Duckcoins.',
        'bourgeois_active': 'Active! {time} left.',
        'bourgeois_recharging': 'Recharging: ready in {time}.',
        'bourgeois_recharge_info': 'Recharges for {minutes} min after buying.',
    },
    'pt': {
        'title': 'Pato vs. Torrada',
        'click_to_play': 'Clique em qualquer lugar para jogar',
        'welcome_back': 'Que bom ter você de volta! Você ficou fora por {time}.',
        'ducks_earned': 'Seus patos ganharam {amount} Duckcoins.',
        'paused': 'Pausado',
        'press_to_continue': 'Aperte Esc ou clique para continuar',
        'victory': 'Você venceu todas as torradas!',
        'toasts_are_back': 'Mas as torradas voltaram... e mais fortes.',
        'keep_playing': 'Clique para continuar jogando',
        'bought': 'Comprados: {count}',
        'siamese_duck': 'Pato Siamês',
        'siamese_duck_effect': 'Soma {dps} de dano por segundo.',
        'double_duck': 'Pato Dobrado',
        'double_duck_effect': 'Dobra o dano do seu clique ({now} -> {next}).',
        'muscular_duck': 'Pato Musculoso',
        'muscular_duck_effect': 'Clica na torrada por você a cada {seconds} s, com o dano do seu clique.',
        'realistic_duck': 'Pato Realista',
        'realistic_duck_effect': 'Dobra todo o dano por segundo ({now} -> {next}).',
        'bourgeois_duck': 'Pato Burguês',
        'bourgeois_duck_effect': 'Por {minutes} min: dano x{damage} e Duckcoins x{coins}.',
        'bourgeois_active': 'Ativo! Faltam {time}.',
        'bourgeois_recharging': 'Recarregando: pronto em {time}.',
        'bourgeois_recharge_info': 'Recarrega por {minutes} min depois de comprar.',
    },
}


def system_language():
    """The computer's language, if the game has it (Portuguese or English)."""
    try:
        name = (locale.getlocale()[0] or '').lower()
    except ValueError:
        name = ''
    return 'pt' if name.startswith(('pt', 'portuguese')) else 'en'


language = system_language()  # the language in use; GameState keeps it in the save


def set_language(new_language):
    global language
    language = new_language if new_language in LANGUAGES else 'en'


def t(key, **values):
    """The text for key in the current language."""
    return TEXTS[language][key].format(**values)
