from duck_vs_toast import i18n, save, shop
from duck_vs_toast.assets import localized
from duck_vs_toast.game import overlay_lines
from tests.helpers import new_game

SIAMESE, DOUBLE, MUSCULAR, REALISTIC = shop.DUCKS


def test_every_text_exists_in_both_languages():
    assert set(i18n.TEXTS['en']) == set(i18n.TEXTS['pt'])


def test_switching_language_changes_the_texts():
    state, _ = new_game()
    assert SIAMESE.title == 'Siamese Duck'
    state.toggle_language()
    assert state.language == 'pt'
    assert SIAMESE.title == 'Pato Siamês'
    assert DOUBLE.describe(state) == 'Dobra o dano do seu clique (1 -> 2).'
    assert overlay_lines('paused')[0] == 'Pausado'
    state.toggle_language()
    assert state.language == 'en' and overlay_lines('paused')[0] == 'Paused'


def test_language_is_saved():
    state, _ = new_game()
    state.set_language('pt')
    data = save.to_dict(state, wall_time=0)
    i18n.set_language('en')
    loaded, _ = new_game()
    save.from_dict(loaded, data, wall_time=0)
    assert loaded.language == 'pt' and i18n.language == 'pt'


def test_unknown_language_falls_back_to_english():
    i18n.set_language('klingon')
    assert i18n.language == 'en'


def test_english_drawings_are_used_when_they_exist():
    sprites = {'nerd_toast': 'pt drawing', 'nerd_toast_en': 'en drawing', 'happy_toast': 'pt only'}
    assert localized(sprites, 'nerd_toast') == 'en drawing'
    assert localized(sprites, 'happy_toast') == 'pt only'  # not drawn in English yet
    i18n.set_language('pt')
    assert localized(sprites, 'nerd_toast') == 'pt drawing'
