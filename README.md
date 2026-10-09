# 🦆 Duck vs. Toast
(or "Pato vs. Torrada")

*A clicker game where ducks battle against evil toasts!*

---

## 📖 About

**Duck vs. Toast** is a clicker game developed entirely in **Python** using **Pygame**.

You begin your journey with a single duck and must defeat increasingly stronger toasts. Earn **Duckcoins**, unlock powerful duck upgrades, and fight your way through endless levels, including challenging boss battles every five levels.

This project was created from scratch, including the programming, game design, balancing, and artwork.

---

## 🎮 Gameplay

- Start with a basic duck that deals **1 click damage**.
- Defeat toasts to earn **Duckcoins**.
- Spend Duckcoins to buy stronger ducks and increase your damage.
- Every level becomes more difficult but rewards more Duckcoins.
- Every **5th level** is a boss battle with a **10-second time limit**.

If you defeat the boss within the time limit, you advance to the next level.

If you fail, the boss's health resets. You can return to previous levels to farm Duckcoins, upgrade your ducks, and try again.

---

## 🦆 Duck Upgrades

### Siamese Duck

- Adds **12.5 DPS** on the first purchase.
- Each purchase adds another **12.5 DPS**.
- Cost increases by **1.5×** each time.

### Double Duck

- Doubles your click damage.
- Every purchase doubles the damage again.
- Cost triples after every purchase.

### Muscular Duck

- Adds an automatic click.
- Automatic clicks scale with your click damage.
- Every purchase reduces the click interval by **50 milliseconds**.
- Cost doubles after every purchase.

### Realistic Duck

- Doubles your total DPS.
- Cost increases by **4×** after each purchase.

### Bourgeois Duck *(Coming Soon)*

Planned abilities:

- Temporary damage boost
- Temporary DPS boost
- Temporary Duckcoin boost

---

## 🍞 Toast Enemies

The game contains **11 different toast enemies**. After the last one, they come back stronger, so the levels never end.

As you progress through the levels, enemies become stronger but also reward more Duckcoins.

Boss toasts appear every five levels and require strategy and upgrades to defeat within the time limit.

---

## 📁 Project Structure

```
Pato-vs.-Torrada/
├── main.py                 # Entry point (run this file)
├── duck_vs_toast/          # Game code
│   ├── config.py           # Screen, colors, positions, timings, balancing
│   ├── levels.py           # Level table: toast, health and reward per level
│   ├── shop.py             # Duck shop: costs and what each duck does
│   ├── state.py            # Game state and rules (damage, DPS, bosses, levels)
│   ├── screen.py           # Everything drawn on screen (including the shop tooltips)
│   ├── numbers.py          # Short numbers: 1500 -> 1.5 K
│   ├── effects.py          # Animations: damage numbers, toast shake, flying coins
│   ├── assets.py           # Loads images and sounds
│   └── game.py             # Main loop and input handling
├── tests/                  # Automated tests (pytest)
├── tools/
│   ├── simulate_balance.py # Virtual player that measures the game's pace
│   └── make_placeholder_icons.py # Draws the temporary sound and next-level icons
├── assets/
│   ├── images/
│   │   ├── ducks/          # Ducks and locked-duck cards
│   │   ├── toasts/         # Toast enemies
│   │   ├── ui/             # Buttons, pointer, boxes
│   │   ├── maps/           # Backgrounds
│   │   └── extras/         # Unused / extra images
│   └── sounds/             # Sound effects
├── requirements.txt
├── requirements-dev.txt    # Extra tools for development (pytest, ruff)
└── README.md
```

**Where to change things:**

- Rebalance the levels (health, rewards, bosses) or add a new toast → `duck_vs_toast/levels.py`, then run the balance simulator (below) to see how long the game takes
- Add a new duck → `duck_vs_toast/shop.py` (plus its images in `assets/images/ducks/`)
- Move a button/text or change a color, timer or the FPS limit → `duck_vs_toast/config.py`
- Make the animations faster, slower or stronger → the "Animations" section of `duck_vs_toast/config.py`
- Give a toast a pained face when it gets hit → draw `<toast name>_hurt.png` (for example `nerd_toast_hurt.png`) in `assets/images/toasts/`, 1280×720 like the normal one; until then the toast just turns reddish
- Change a duck's tooltip text → its `..._description` function in `duck_vs_toast/shop.py`
- Replace the temporary icons (`sound_on`, `sound_off`, `next_level_on`, `next_level_off` in `assets/images/ui/`) → draw your own 1280×720 images with the same names, with the icon in the same spot

---

## 💻 Technologies

- Python 3
- Pygame

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/Duck-vs.-Toast.git
```

Or download the project as a ZIP file and extract it.

### 2. Open the project

Open the extracted folder in **Visual Studio Code** (or your preferred Python IDE).

### 3. Install Python

If Python is not installed, download it from:

https://www.python.org/downloads/

Make sure Python is added to your system PATH.

### 4. Install Pygame

Open a terminal inside the project folder and run:

```bash
pip install -r requirements.txt
```

### 5. Run the game

Execute:

```bash
python main.py
```

Or simply run **main.py** using Visual Studio Code.

### Or play in GitHub Codespaces

1. On the repository page, click **Code → Codespaces → Create codespace**.
2. Wait for the setup to finish (it installs Pygame automatically).
3. Open the **Ports** tab, find port **6080** and click the 🌐 icon to open the desktop in a new browser tab. Click **Connect** and use the password `vscode`.
4. Back in the Codespaces terminal, run `python main.py`. The game window appears in the desktop tab.

> Codespaces has no sound, so the game runs without the quack.

---

## 🧪 Tests and balance

Install the development tools once:

```bash
pip install -r requirements-dev.txt
```

Run the automated tests:

```bash
pytest
```

See how long the game takes, level by level, with a virtual player:

```bash
python -m tools.simulate_balance
```

The tests also run automatically on GitHub (in the **Actions** tab) every time code is pushed.

---

## 🎯 Controls

| Action | Key |
|---------|-----|
| Attack | Left Mouse Button |
| Mute / unmute the quack | M (or the speaker button, top right) |
| Go back / forward a level | `<` and `>` buttons next to the level (forward only to levels already beaten) |
| See what a duck does | Hover the mouse over it in the shop |
| Cheat: +1 T Duckcoins (only with `DEV_MODE = True` in `duck_vs_toast/config.py`) | P |

---

## 💰 Currency

The in-game currency is **Duckcoin**.

Duckcoins are earned by defeating toasts and can be spent to purchase duck upgrades.

---

## ✨ Features

- Clicker gameplay
- Automatic and manual damage
- Multiple upgradeable ducks
- Progressive difficulty
- Boss battles
- Duckcoin economy
- Farming previous levels
- Endless levels (about 1 hour to see every toast)
- 11 unique toast enemies

---

## 🛠 Future Features

Ideas for the future are collected in **[IDEAS.md](IDEAS.md)**.

---

## 💡 What I Learned

This project helped me practice:

- Object-Oriented Programming
- Game loops
- Event handling
- Collision detection
- UI development with Pygame
- Game balancing
- Upgrade systems
- Saving and managing game state
- Structuring larger Python projects

---

## 🎨 Inspiration

The gameplay was mainly inspired by:

- Clicker Heroes
- Duck Pond

---

## 👨‍💻 Author

Developed entirely by me.

Everything in this project—including programming, gameplay mechanics, balancing, art, and game design—was created from scratch as a personal learning project.
