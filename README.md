# A* Pathfinding - Path Planning with Random Obstacles

A comprehensive A* pathfinding application featuring two robot movement models (point and square), real-time visualization, performance metrics, and dynamic theme support.

---

## 🎯 Features

### Core Requirements
- **Explored Area Visualization** - Real-time visualization of open (green) and closed (red) nodes.
- **Final Path Display** - Path visualization adjusted for the specific robot footprint.
- **Performance Metrics** - Comprehensive tracking of search time, path cost, and exploration efficiency.
- **2+ Movement Models** - Support for Point robot (1×1) and Square robot (2×2, 3×3) with footprint validation.
- **Dynamic Obstacles** - Tools for random obstacle generation and manual grid editing.
- **Model Switching** - Buttons to switch between robot sizes
- **Regenerate Obstacles** - Random generation, maze generation, and clear grid
- **Run Planner** - A* with 4-directional and diagonal movement
- **Comparison Table** - Side-by-side analysis of different runs to evaluate algorithm performance.

### Additional Functionality
- **Three Visual Themes** - Carrot Hunt, Dungeon Escape, and Obstacle Course with custom robot icons
- **Weighted Terrain** - Add high-cost areas (5× cost) using Ctrl+Drag or brush tool
- **Robot Animation** - Smooth step-by-step movement along the final path
- **Live Node Information** - Hover over cells to see g(n), h(n), f(n), and weight values
- **Maze Generation** - Procedural maze creation using recursive backtracker
- **Search Effectiveness Score** - Composite metric combining exploration efficiency, time, and optimality

---


## 🚀 Quick Start

### Requirements
```bash
Python 3.10+
customtkinter   # pip install customtkinter
Pillow          # pip install Pillow
```

### Run the Application
```bash
python astar_pathfinding_tk.py
```

### Controls
- **Left-click:** Place start → end → obstacles
- **Right-click:** Erase cells
- **Drag:** Draw obstacles
- **Ctrl+Drag:** Paint weighted terrain (high-cost areas)
- **Keys 1, 2, 3:** Switch between themes
- **Buttons:** Change robot size, regenerate obstacles, run pathfinding

---

## 📋 How It Works

### A* Algorithm
- **Heuristic:** Manhattan distance (informed search)
- **Cost Formula:** g(n) = g(previous) + (move_cost × terrain_weight)
- **Priority Queue:** Heapq with O(log n) insertion
- **Goal Detection:** Checks if ANY cell of robot footprint touches goal

### Robot Movement Models

**Point Robot (1×1)**
- Single cell occupancy
- Can fit through 1-cell gaps
- Optimal for open spaces

**Square Robot (2×2, 3×3)**
- Rigid body (no rotation)
- All cells in footprint must be walkable
- Cannot squeeze through tight gaps
- Requires 2×2 or 3×3 clear space

**Footprint Validation:**
```python
for dr in range(robot_size):
    for dc in range(robot_size):
        # Check all cells in robot footprint
        if grid[row+dr][col+dc].is_barrier():
            return False  # Cannot fit here
return True  # Safe to place robot
```

### Comparison Metrics
The comparison table tracks:
1. **Model** - Robot type (Point/Square)
2. **Path Length** - Total distance traveled
3. **Nodes Explored** - How many nodes searched
4. **Time (ms)** - Execution time in milliseconds
5. **Peak Priority Queue** - Memory usage (cells in queue at peak)
6. **Space Complexity** - Nodes in closed set
7. **ADS2 Efficiency%** - (Total_Walkable - Explored) / Total_Walkable × 100

**Color Coding:**
- 🟢 Green ↓ = Better (less cost)
- 🔴 Red ↑ = Worse (more cost)
- ⚪ Grey ≈ = Similar (<5% difference)

---

## 📁 Project Structure

```
PathPlanning_Projekat/
├── astar_pathfinding_tk.py          # Main application (1841 lines)
├── theme_manager.py                 # Theme configuration
├── README.md                         # This file
├── ATTRIBUTION.md                   # Icon credits & licenses
├── FINAL_SUBMISSION_CHECK.md        # Complete requirement verification
├── REQUIREMENTS_VERIFICATION.md     # Detailed requirement checklist
└── themes/                          # Visual theme assets
    ├── rabbit/                      # Cute rabbit theme 
    │   ├── robot.png
    │   ├── obstacle.png
    │   └── goal.png
    ├── space/                       # Spaceship theme 
    │   ├── robot.png
    │   ├── obstacle.png
    │   └── goal.png
    └── escape/                      # Dungeon escape theme 
        ├── robot.png
        ├── obstacle.png
        └── goal.png
```

---

##  Themes

Rabbit Theme 🐰: Designed for simple grid visualization.

    Robot: Pixel Rabbit sprite.

    Goal: Carrot.

    Obstacles: Shrubs.

Space Theme 🚀: High-contrast mode for clear path visibility.

    Robot: Spaceship.

    Goal: SThe earth.

    Obstacles: Asteroids.

Dungeon Escape 🔐: Focuses on weighted terrain visualization.

    Robot: Prisoner/Escapee.

    Goal: Exit Door.

    Obstacles: Prison bars.

---

## 📊 Performance Metrics Explained

###  Efficiency Formula
```
Efficiency% = ((Total_Walkable_Cells - Nodes_Explored) / Total_Walkable_Cells) × 100
```
- **High efficiency (>80%)** = Excellent search, avoided most of the grid
- **Medium efficiency (50-80%)** = Good search, explored selective areas
- **Low efficiency (<50%)** = Broad search, explored much of the grid

### Peak Priority Queue
- **Memory usage indicator** for the A* algorithm
- Shows maximum size of the open set during search
- Useful for understanding space complexity in practice

---

##  Weighted Terrain System

### How It Works
- **Normal terrain:** Cost = 1 (or √2 for diagonal)
- **High-cost terrain:** Cost = 5× (or 5√2 for diagonal)
- **Path behavior:** Algorithm avoids weighted terrain unless necessary

### How to Use
**Method 1: Paint with Brush**
1. Enable "High-Cost Brush" checkbox
2. Drag to paint weighted cells (appears as pink overlay)

**Method 2: Ctrl+Drag**
1. Hold Ctrl and drag on the grid
2. Creates weighted terrain cells automatically

**Method 3: Random Weights**
1. Click " Random Weights" button
2. Automatically adds 10-20% weighted terrain

### Visual Indicator
- Pink semi-transparent overlay with red border
- Shows which cells have high cost
- Path will show increased length when traversing these cells


---

## 📝 Attribution

This project uses free icons from **Flaticon.com** and **PNGtree.com**.

All icons are properly licensed for educational and commercial use.

**See [ATTRIBUTION.md](ATTRIBUTION.md) for detailed credits and license information.**

---

## 🐛 Troubleshooting

### Application Won't Start
```bash
# Install missing dependencies
pip install customtkinter Pillow
```

### No Icons Showing
- Ensure `themes/` folder exists in the same directory
- Check that PNG files are present in theme folders
- Try switching themes (press 1, 2, or 3)

### Pathfinding Too Slow
- Reduce grid size or obstacle density
- Try 4-directional movement (faster than diagonal)

---

##  Learning Resources

This project demonstrates:
- **Algorithm:** A* pathfinding with heuristic search
- **Data Structures:** Priority queues (heapq), sets, dictionaries
- **GUI Programming:** CustomTkinter for modern UI
- **Image Processing:** Pillow for PNG loading and scaling
- **Game Development:** Sprite positioning, animation, theme systems
- **Algorithms & Data Structures Course Concepts:**
  - Time complexity analysis
  - Space complexity measurement
  - Heuristic-guided search
  - Weighted graphs
  - Grid-based pathfinding

---


##  Author
**Student:** Džana Kopić 
**Index:** 20165 
**Course:** Algorithms and Data Structures II (ADS2)  
**Institution:** Faculty of Electrical Engineering (ETF Sarajevo)

##  Acknowledgments
- **Mentorship:** Doc. dr. Sead Delalić 
- **Framework:** CustomTkinter (Modern UI for Python)
- **Assets:** Icons from Flaticon & PNGtree

