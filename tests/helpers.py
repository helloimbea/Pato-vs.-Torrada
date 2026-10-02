from duck_vs_toast.state import GameState


class FakeClock:
    """A clock we control, in milliseconds."""

    def __init__(self):
        self.now = 0

    def __call__(self):
        return self.now


def new_game(duckcoins=0):
    clock = FakeClock()
    state = GameState(clock=clock)
    state.duckcoins = duckcoins
    return state, clock
