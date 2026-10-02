import pytest

from duck_vs_toast.screen import format_number


@pytest.mark.parametrize('number, text', [
    (0, '0'),
    (12.5, '12.5'),
    (25.0, '25'),
    (999, '999'),
    (1500, '1.5 K'),
    (999960, '1 M'),
    (2 * 10**12, '2 T'),
    (10**22, '10 Sx'),
])
def test_format_number(number, text):
    assert format_number(number) == text
