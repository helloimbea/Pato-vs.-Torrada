from duck_vs_toast import levels


def test_each_toast_lasts_five_levels_starting_as_boss():
    first, second = levels.TOASTS[:2]
    assert [levels.toast_for(level) for level in (1, 4)] == [first] * 2
    assert levels.toast_for(5) == second
    assert levels.toast_for(54) == levels.TOASTS[-1]


def test_toasts_cycle_after_the_last_one():
    assert levels.toast_for(55) == levels.TOASTS[0]
    assert levels.toast_for(60) == levels.TOASTS[1]


def test_bosses_every_five_levels():
    assert [level for level in range(1, 21) if levels.is_boss(level)] == [5, 10, 15, 20]


def test_normal_levels_always_get_harder_and_pay_more():
    normal = [level for level in range(1, 200) if not levels.is_boss(level)]
    for previous, level in zip(normal, normal[1:], strict=False):
        assert levels.health_for(level) > levels.health_for(previous)
        assert levels.reward_for(level) > levels.reward_for(previous)


def test_boss_is_harder_and_pays_more_than_the_levels_around_it():
    for boss in range(5, 200, 5):
        for neighbor in (boss - 1, boss + 1):
            assert levels.health_for(boss) > levels.health_for(neighbor)
            assert levels.reward_for(boss) > levels.reward_for(neighbor)


def test_get_level_returns_toast_health_and_reward():
    assert levels.get_level(1) == (levels.TOASTS[0], levels.STARTING_HEALTH, levels.STARTING_REWARD)
