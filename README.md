<div align="center">

# 🎮 Python Game Collection

### A comprehensive showcase of Python programming featuring interactive games built with Pygame

[![Python Version](https://img.shields.io/badge/python-3.11-blue.svg?style=for-the-badge&logo=python&logoColor=white&color=%23FF006E)](https://python.org)
[![Pygame Version](https://img.shields.io/badge/pygame-2.6.1-black.svg?style=for-the-badge&logo=python&logoColor=white&color=%238B5CF6)](https://pygame.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg?style=for-the-badge&logo=open-source-initiative&logoColor=white&color=%2300D9FF)](LICENSE)
[![Status](https://img.shields.io/badge/status-Complete-success.svg?style=for-the-badge&logo=github&logoColor=white&color=%23FF006E)](https://github.com)

<br/>

</div>

---

## 📖 About

This **Python Game Collection** is an accumulation of every game project from **CMPS-455**, a game programming course aimed at utilizing Python at Southeastern Louisiana University. The collection features 7 distinct programs that progressively build programming skills from basic algorithms to complex game mechanics, demonstrating fundamental programming concepts, game development principles, and advanced graphical games with physics, AI, and user interaction.

---

## 🌟 Key Features

- **🎯 Number Guessing Games** - Interactive console games with intelligent algorithms
- **🎨 Graphics Demonstrations** - Pygame-based visual applications with mouse interaction
- **⭕ Tic-Tac-Toe** - Complete implementation with both console and graphical versions
- **🏓 Advanced Pong** - Multiplayer pong with shooting mechanics and AI opponent
- **🚀 Asteroids** - Full-featured space shooter with physics and collision detection
- **🤖 AI Integration** - Computer opponents with varying difficulty levels
- **⚡ Real-time Graphics** - Smooth animations and responsive user interfaces

---

## 🛠 Tech Stack

### Languages

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white&color=%23FF006E)](https://python.org)

### Frameworks & Libraries

[![Pygame](https://img.shields.io/badge/Pygame-2.6.1-000000?style=for-the-badge&logo=python&logoColor=white&color=%238B5CF6)](https://pygame.org)

### Development Tools

[![Pip](https://img.shields.io/badge/pip-22.3-3776AB?style=for-the-badge&logo=python&logoColor=white&color=%2300D9FF)](https://pip.pypa.io/)
[![Virtual Environment](https://img.shields.io/badge/venv-Active-4B8BBE?style=for-the-badge&logo=python&logoColor=white&color=%23FF006E)](https://docs.python.org/3/library/venv.html)

---

## 🏗 Architecture

This collection follows a **modular design** with each program as a standalone executable demonstrating specific programming concepts:

```
📁 Python Game Collection
├── 🎯 program1.py - User guesses computer's number (console)
├── 🧠 program2.py - Computer guesses user's number (console)
├── 🎨 program3.py - Graphics demo with interactive elements
├── ⭕ program4.py - Tic-Tac-Toe console version with AI
├── 🎮 program5.py - Tic-Tac-Toe graphical version with AI
├── 🏓 program6.py - Advanced Pong with shooting mechanics
├── 🚀 program7.py - Asteroids space shooter game
├── 📁 venv/ - Python virtual environment
├── 📁 public/ - Game assets (images)
└── 📁 submissions/ - Course assignment documentation
```

Each program demonstrates **increasing complexity** from basic algorithms to advanced game development with physics, collision detection, and AI.

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11** or higher
- **pip** package manager
- **Git** (optional, for cloning)

### Installation

1. **Clone or Download** the repository:

   ```bash
   git clone <repository-url>
   cd cmps-455
   ```

2. **Set up Virtual Environment** (recommended):

   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   _Note: If requirements.txt doesn't exist, install Pygame manually:_
   ```bash
   pip install pygame==2.6.1
   ```

### Running the Games

Each program can be run independently:

```bash
# Number guessing games
python program1.py  # User guesses computer's number
python program2.py  # Computer guesses user's number

# Graphics demonstration
python program3.py  # Interactive drawing application

# Tic-Tac-Toe games
python program4.py  # Console version
python program5.py  # Graphical version

# Advanced games
python program6.py  # Pong Shootout
python program7.py  # Asteroids
```

---

## 📚 API Documentation

### Game Classes & Functions

#### Tic-Tac-Toe Implementation (`program4.py`, `program5.py`)

- **`build_win_masks()`** - Creates winning condition bitmasks
- **`has_won(player_mask)`** - Checks for winning conditions
- **`random_ai_move()`** - Implements basic AI opponent
- **`cell_empty()`** - Validates move legality

#### Pong Shootout (`program6.py`)

- **`update_ball()`** - Physics-based ball movement
- **`check_ball_paddle_collisions()`** - Collision detection
- **`ai_move()`** - Computer opponent logic
- **`shoot_bullet()`** - Projectile system

#### Asteroids (`program7.py`)

- **`create_asteroid()`** - Procedural asteroid generation
- **`update_ship()`** - Ship physics and controls
- **`check_asteroid_collisions()`** - Multi-object collision detection
- **`check_bullet_asteroid_collisions()`** - Projectile-asteroid interactions

---

## 📁 Project Structure

```
📦 Python Game Collection
├── 📄 program1.py           # Number Guessing (User vs Computer)
├── 📄 program2.py           # Number Guessing (Computer vs User)
├── 📄 program3.py           # Graphics Demo (AP Letters + Football)
├── 📄 program4.py           # Tic-Tac-Toe (Console)
├── 📄 program5.py           # Tic-Tac-Toe (Graphical)
├── 📄 program6.py           # Pong Shootout (Advanced)
├── 📄 program7.py           # Asteroids (Space Shooter)
├── 📁 venv/                 # Python Virtual Environment
│   ├── 📁 Include/         # C Headers
│   ├── 📁 Lib/            # Python Libraries
│   └── 📄 pyvenv.cfg       # Environment Config
├── 📁 public/              # Game Assets
│   └── 🖼️ bk-headshot.jpg  # Asteroid Texture
└── 📁 submissions/         # Course Materials
    ├── 📄 assignment1.pdf
    ├── 📄 assignment2.pdf
    ├── 📄 assignment3.pdf
    ├── 📄 assignment4.pdf
    └── 📄 assignment5.pdf
```

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

**Permissions:**

- ✅ Commercial use
- ✅ Modification
- ✅ Distribution
- ✅ Private use

**Limitations:**

- ❌ Liability
- ❌ Warranty

---

<div align="center">

**Built with ❤️ using Python & Pygame**

[![Made with Python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg?style=for-the-badge&logo=python&logoColor=white&color=%23FF006E)](https://python.org)
[![Powered by Pygame](https://img.shields.io/badge/Powered%20by-Pygame-000000.svg?style=for-the-badge&logo=python&logoColor=white&color=%238B5CF6)](https://pygame.org)

_CMPS-455 Programming Course Project_

</div>
