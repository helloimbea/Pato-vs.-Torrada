"""Guards the game's pace: if a change makes the game much faster or slower, this fails.

If you rebalance on purpose, run `python -m tools.simulate_balance` and update the limits.
"""
from tools.simulate_balance import simulate


def test_reaching_level_54_takes_about_an_hour():
    reached = simulate(target_level=54, max_minutes=120)
    assert 54 in reached, f'the virtual player got stuck on level {max(reached)}'
    assert 40 <= reached[54] <= 75
