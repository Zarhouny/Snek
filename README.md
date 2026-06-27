# 🐍 Snek

A fully playable Snake game written from the ground up in Python. You can play it yourself like a classic arcade game, or turn on AI-MODE to watch a model demonstrate it's Machine Learning capabilities to master the grid from scratch.

---

## 📝 Introduction

Most Snake projects use pre-programmed pathfinding tricks to beat the game. This project does something different: it drops a blank digital brain into the game with no prior instructions, forces it to learn from its own mistakes, and watches it figure out how to survive.

*Because **snek** is built as a complete customizable sandbox, you can change the look, tweak the rules, turn off wall collisions, or let the AI take over the controls to see how it reacts to your changes.*

---
## How to Play:

**`Left Arrow`** to turn left. ⬅️

**`Right Arrow`** to turn Right. ➡️

**`Up Arrow`** to go Up. ⬆️

**`Down Arrow`** to go Down. ⬇️

**`Space`** to Reset the Run. 📸

**`Esc`** to pause the game. ⏸️





## 🛠️ Customization

All the settings are sitting right at the top of your `main.py` file. You can change the entire behavior of the game just by swapping out a few numbers or words.

### 1. Visuals & Window Size
* **`WIDTH, HEIGHT = 500, 500`**
    * *What it does:* Sets the size of the game window in pixels. 
    * *How to tweak it:* Keep them as multiples of your `SPACE_SIZE` (like 400, 600, 800) so the grid aligns perfectly.

* **`SPACE_SIZE = 20`**
    * *What it does:* This is the size of a single grid block. It controls how thick Snek is and how big the food is.
    * *How to tweak it:* Lowering this to `10` makes the game tiny and gives Snek a massive board to play on. Raising it to `50` makes Snek huge and the board incredibly cramped.
* **`show_grid = True`**
    * *What it does:* Draws the grey grid lines on the board. Set it to `False` if you want a clean, retro look without lines.
* **Hex Colors (`SNAKE_COLOR`, `FOOD_COLOR`, `BACKGROUND_COLOR`, `GRID_COLOR`)**
    * *What it does:* Controls the color theme of your game using standard hex codes. Swapping `#ffffff` to `#121212` for the background will instantly give you a dark mode.


### 2. Game Rules & Modes
* **`infinite_space = False`**
    * *What it does:* Determines if Snek can phase through walls. 
    * *How to tweak it:* Change this to `True` to activate **Border Wrapping**. If Snek goes off the left edge of the screen, it will instantly pop out on the right edge. 
* **`OUROBOROS_MODE = False`**
    * *What it does:* Determines if Snek can phase through herself.
    * *How to tweak it:* If you switch this to `True`, Snek a ghost to itself—it can pass right through its own tail without dying. 


### 3. AI Activation & Speed
* **`AI_ENABLED = True`**
    * *What it does:* The master toggle for the AI.
    * *How to tweak it:* Set it to `False` if you want to play the game yourself using the arrow keys. Set it to `True` to let the AI take over.
* **`SPEED_STEP = 2`**
    * *What it does:* Controls how fast the game speeds up when a *human* is playing. Every time you eat 10 apples (defined by this step), the game gets faster. (Note: When the AI is playing, it automatically runs at maximum speed so it can train faster).

---

## 🧪 Proof of Concept (AI Mode)

When you activate the AI feature, Snek goes through distinct evolutionary stages as it trains:

| Training Phase | High Score Range | Behavioral Traits |
| :--- | :--- | :--- |
| **Games 0 – 50** | $0 - 5$ | Complete chaos. Snek makes random wild guesses to see how the board works. |
| **Games 50 – 150** | $5 - 60$ | Figures out how to dodge walls, but constantly rams into its own body out of greed. |
| **Games 150 – 300** | $60 - 90$ | Learns to respect its own tail; starts making careful, fluid loops. |
| **Games 300+** | **110+** | Random guessing shuts off completely. The Snek acts on pure instinct, packing its body perfectly to break into triple digits. |

❗ a startring **`Snake_brain.pth`** file has been included within the game files. a collection of 517 games the AI has played and learned from with a high score of 133. if you want to train it from scratch, delete the file.
<br>

<p align="center">
  <img src="https://github.com/user-attachments/assets/a8a2073f-3e54-4f81-b7f7-16f0846d9638" alt="showcase" width="300" />
</p>

<br>


## ❓ FAQ

### Why use Machine Learning instead of using some modified version of Search algorithms like A* or BFS?

```red
How about you be less of a coward.
```


## 📖 Documentation

### 1. Sight Vector (What the AI Sees)
When the AI feature is turned on, it evaluates the board using 8 sightlines cast out at $45^\circ$ angles relative to its current heading. Because these lines are relative, what it learns while moving Up instantly applies when it turns Left or Right

1. **Forward** | 2. **Backward** | 3. **Left** | 4. **Right** | 5. **4 Diagonals**

Each line tracks exactly **3 things**, totaling 24 data inputs for the brain:
* **Wall Distance:** How close a wall is. Closer boundaries send a stronger danger signal
* **Tail Distance:** How close its own body segments are
* **Food Location:** A simple switch that flips on if an apple is directly in that line of sight

### 2. Tuning the Brain's Code Settings (Inside `ai.py`)
If you want to change how the AI learns, look at how the `Agent` is set up inside `ai.py`:
* **`lr=0.0003` (Learning Rate):** How drastically the brain updates its memory when it makes a mistake. If you make this too high, it panics and forgets everything; too low, and it takes thousands of games to learn anything useful.
* **`gamma=0.9` (Discount Factor):** Tells the AI how much it should care about future survival versus immediate rewards. `0.9` means it values keeping the board open over just greedily rushing the closest apple.
* **The Feedback Policy (Rewards & Punishments):** The brain learns by chasing a high score built into the code:
    * *Crashing (Death):* $-10.0$ points
    * *Eating an Apple:* $+10.0$ points
    * *Moving Closer to an Apple:* $+0.15$ points
    * *Moving Away from an Apple:* $-0.25$ points
    * *Stagnation Loop Penalty:* $-0.50$ points per step if it wastes more than 60 moves without eating (stops it from spinning in endless safe circles).

---

## 🛠️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Zarhouny/snek.git
   cd snek
   ```
2. **Install Dependencies:**
   *( Ensure you have Python 3.8+ installed: )*
    ```bash
    pip install torch
    ```
3. **Run the Project:**
   ```bash
   python snake.py
   ```

## 👤 Author
* Moslim Zarhouni - [@Zarhouny](https://github.com/Zarhouny)
