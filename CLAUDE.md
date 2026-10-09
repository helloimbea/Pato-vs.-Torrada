# CLAUDE.md

Context for Claude (in VS Code, Claude Code or anywhere else) working on this game.

## About the person

- The owner speaks **Portuguese** and is not a programmer. Reply in Portuguese, in plain words,
  and explain any Git/GitHub step (pull request, merge, pull) one click at a time.
- Code, comments, file names and commit messages stay in **English**.
- The art (ducks, toasts, buttons) is drawn by the owner. Don't redraw it; when something new
  needs an icon, draw a simple placeholder in code and say it is temporary.

## The game

**Duck vs. Toast** (Pato vs. Torrada): a clicker made with Python + Pygame, 1280×720, 30 FPS.
Ducks attack toasts, toasts pay Duckcoins, Duckcoins buy more ducks. Every 5th level is a boss
with a 10 s timer. Levels never end (after the last toast they loop back, stronger).

```
main.py                    entry point
duck_vs_toast/
  config.py                screen, colors, positions, timings, DEV_MODE
  levels.py                level formulas (6 balancing numbers at the top)
  shop.py                  ducks: cost, effect and tooltip text
  state.py                 game state and rules (damage, DPS, bosses, levels, mute)
  screen.py                everything drawn on screen (incl. tooltips)
  layout.py                resizable window: offset of each screen part, mouse -> part coords
  save.py                  save/load JSON (~/.duck_vs_toast/save.json), offline earnings
  clock.py                 GameClock: game time that stops while paused
  i18n.py                  texts written by code, English + Portuguese; t('key')
  numbers.py               short numbers: 1500 -> "1.5 K"
  effects.py               animations: damage numbers, toast shake, flying coins
  assets.py                loads images and sounds
  game.py                  main loop, clicks and keys
tools/simulate_balance.py  virtual player that measures the game's pace
tools/make_placeholder_icons.py  temporary sound / next-level icons
tools/crop_images.py       crops full-screen drawings, saves positions
tests/                     pytest tests
assets/images/...          art, cropped to the drawing; assets/images/positions.json says where each goes
IDEAS.md                   the owner's notepad of future ideas (theirs to edit)
```

## Commands

```bash
pip install -r requirements-dev.txt   # pygame, pytest, ruff
python main.py                        # play
pytest                                # tests (must pass)
ruff check .                          # code style (must pass)
python -m tools.simulate_balance      # how long the game takes, level by level
```

GitHub Actions runs ruff, pytest and the simulator on every push (`.github/workflows/tests.yml`).
Before pushing, run `ruff check .` and `pytest`. If a change touches balance, run the simulator
and say how the pace changed (today: level 54 in about 55 minutes).

## Decisions already made

- No Replit (its files were removed).
- DPS damage is applied once per second, and the number on screen is the real damage per second.
- The muscular duck's auto-click always uses the current click damage.
- Levels are endless; health and reward come from formulas in `levels.py`, not a table.
- `DEV_MODE = False` in `config.py`; turning it on enables the P cheat and prints click positions.
- Only the left mouse button does anything; the quack plays only when hitting the toast or a button.
- Sound and next-level icons are placeholders until the owner draws their own
  (same file names in `assets/images/ui/`).
- Images are cropped to the drawing, and `assets.py` loads each as a `Sprite` (image + position).
  The owner draws on a 1280×720 canvas in the right spot and runs `python -m tools.crop_images`;
  the game also accepts an uncropped full-screen image. Maps (backgrounds) stay full-screen.
- The bread slice is painted on the old map; until the owner draws `toasts/bread.png` (and a map
  without the bread), `assets.split_bread` cuts it out at startup so it can squash with the face. A pained face is an optional `<toast>_hurt.png` the owner
  draws; until it exists, the toast turns reddish while hurt. Likewise `<toast>_dead.png` is the face of a
  beaten toast as it shrinks away (gray tint until drawn); the next toast pops up meanwhile.
- A bought duck stretches and squashes (and a new one grows in), via `GameState.on_buy`.
- The window is resizable. Art and positions stay in 1280×720 coordinates; `layout.py` pins four
  parts to the window (`top_left` stats, `top_right` level/sound buttons, `center` toast and ducks,
  `bottom` shop), and the canvas is scaled to fit. `assets.py` splits the map into background,
  stats boxes and shop panel; `screen.stretch` widens the background and shop without
  stretching the drawing. Clicks use `layout.to_group(part, mouse_pos)`.
- Saving: autosave every 30 s and on close; old saves keep defaults for new fields. Offline
  earnings: the ducks (DPS + muscular duck, no clicks) keep beating the current level's toast
  (the one before it on a boss level) for up to 8 h; owner chose 8 h.
- Bourgeois Duck (owner's design): fixed price 10 M, for 1 min doubles all damage and toast
  Duckcoins, then 10 min recharge from purchase. Not in `shop.DUCKS`; see `shop.buy_bourgeois`.
- Screens: start (with "welcome back" earnings), pause (Esc), victory once all toasts are beaten
  (`state.has_won`, shown once). They are text drawn by code in `game.py`; the game clock is
  paused behind them.
- Languages (owner asked 2026-10-09): English and Portuguese, switched with L or the EN/PT button
  (placeholder icons `ui/language_en.png`, `ui/language_pt.png`), saved with the progress; first run
  uses the computer's language. Code text lives in `i18n.py` (every key in both languages; tests
  run in English via `tests/conftest.py`). The current drawings are the Portuguese ones; an English
  drawing is the same name + `_en` (`assets.localized`; maps: `maps/map1_en.png`), falling back to
  the Portuguese drawing until the owner draws it.

## Plan and progress

Each phase is one pull request into `main`; the owner reviews and merges it on GitHub.

- [x] **Phase 0:** reorganize into modules, translate code to English, Codespaces setup.
- [x] **Phase 1:** quick fixes (DEV_MODE, left click only, short numbers, DPS, muscular duck).
- [x] **Phase 2:** tests, GitHub Actions, formula-based endless levels, balance simulator.
- [x] **Phase 3:** mute (M key and button), next-level button, purchase counters, duck tooltips.
- [x] **Phase 4:** damage numbers floating up, toast shaking and squashing (with a pained face) when hit, coins flying when a toast is beaten; later: beaten toast shrinks away, bought ducks stretch.
- [x] **Phase 5:** save progress to JSON (autosave and on close), Duckcoins earned while closed
  (up to 8 h), start/pause (Esc)/victory screens, Bourgeois Duck.
- [ ] **Phase 6 (next):** ~~crop the full-screen images~~ (done early, with Phase 4); ~~language switch~~ (done);
  English versions of the drawings with text (owner draws `_en` files).
- [ ] **Phase 7:** browser version with `pygbag` for itch.io; Windows `.exe` with PyInstaller.

When a phase is done, tick it here in the same pull request.

## Getting changes to the owner's computer

After a pull request is merged on GitHub, the owner opens **GitHub Desktop**, picks this
repository, makes sure the branch is `main`, and clicks **Fetch origin** and then **Pull origin**.
