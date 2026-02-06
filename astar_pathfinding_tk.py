# A* Pathfinding with themes and robot movement
# Uses customtkinter for GUI and PIL for images

import tkinter as tk
from tkinter import ttk, filedialog
import customtkinter as ctk
import math
import random
import time
import heapq
from PIL import Image, ImageTk
import os
from pathlib import Path

# Configure CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Import theme manager
import sys
sys.path.insert(0, str(Path(__file__).parent))
from theme_manager import ThemeManager, ThemeConfig

# Window dimensions
WIDTH = 800
ROWS = 50
CELL_SIZE = WIDTH // ROWS

# Default colors (will be overridden by themes)
WHITE = "#FFFFFF"
BLACK = "#2C3E50"
RED = "#E74C3C"
GREEN = "#2ECC71"
BLUE = "#3498DB"
YELLOW = "#F1C40F"
PURPLE = "#9B59B6"
ORANGE = "#E67E22"
GREY = "#BDC3C7"
TURQUOISE = "#1ABC9C"
LIGHT_BLUE = "#ECF0F1"
DARK_GREY = "#34495E"

# Theme-driven globals (updated dynamically)
BACKGROUND_COLOR = LIGHT_BLUE
EMPTY_COLOR = WHITE
PATH_COLOR = TURQUOISE
OPEN_COLOR = GREEN
CLOSED_COLOR = RED
WEIGHT_COLOR = "#E74C3C"
WEIGHT_VALUE = 5
WEIGHT_STIPPLE = "gray35"

# Theme colors - gets overridden when you switch themes
THEME_CONFIG = {
    "rabbit": {
        "name": "Carrot Hunt",
        "canvas_bg": "#B8D4E8",         # Medium light cyan-blue (clearly not white)
        "grid_line": "#7CB0C8",         # Medium blue-grey
        "obstacle": "#2C3E50",          # Dark navy
        "path": "#1ABC9C",              # Turquoise
        "explored": "#2ECC71",          # Green
        "weight": "#4AA3DF",            # Water blue (high-cost)
        "accent": "#90EE90"             # Light green
    },
    "space": {
        "name": "space",
        "canvas_bg": "#000000",         # Pure black
        "grid_line": "#1E2A3A",         # Dark grey-blue
        "obstacle": "#2C3E50",          # Navy grey
        "path": "#00D4FF",              # Neon blue
        "explored": "#39FF14",          # Neon green
        "weight": "#8A2BE2",            # Glowing purple (space dust)
        "accent": "#4169E1"             # Royal blue
    },
    "escape": {
        "name": "Dungeon Escape",
        "canvas_bg": "#7a6a5a",         # Lighter brown-grey for visibility
        "grid_line": "#3a3a3a",         # Dark grey grid lines
        "obstacle": "#2c2c2c",          # Dark obstacles (will be visible)
        "path": "#FFD700",              # Gold
        "explored": "#FFA500",          # Orange
        "weight": "#DC143C",            # Crimson (guards)
        "accent": "#8B4513"             # Brown
    }
}

# Maze generation using recursive backtracking
# Makes corridors wide enough for the robot to fit
def generate_maze(grid, robot_size=1, preserve_nodes=None):
    if preserve_nodes is None:
        preserve_nodes = set()
    
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    
    # Calculate corridor width to fit robot
    corridor_width = max(2, robot_size + 1)  # At least robot_size + 1
    step = 2 * corridor_width  # Standard maze step: 2x corridor for walls+passage
    
    # Reset all cells to walls (except preserved nodes)
    for row in range(rows):
        for col in range(cols):
            if (row, col) not in preserve_nodes:
                grid[row][col].color = BLACK
                grid[row][col].weight = 1
    
    # Visited set for backtracking
    visited = set()
    
    def carve_passage(row, col):
        """Recursively carve passages through the maze"""
        visited.add((row, col))
        
        # Directions: up, right, down, left (shuffled for randomness)
        directions = [(0, -step), (step, 0), (0, step), (-step, 0)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            next_row = row + dy
            next_col = col + dx
            
            # Check bounds
            if 0 <= next_row < rows and 0 <= next_col < cols:
                if (next_row, next_col) not in visited:
                    # Carve the wall between current and next cell
                    wall_row = row + (dy // abs(dy)) if dy != 0 else row
                    wall_col = col + (dx // abs(dx)) if dx != 0 else col
                    
                    # Clear the main passage and corridor area (skip preserved nodes)
                    for r in range(max(0, min(row, next_row) - corridor_width // 2),
                                   min(rows, max(row, next_row) + corridor_width // 2 + 1)):
                        for c in range(max(0, min(col, next_col) - corridor_width // 2),
                                      min(cols, max(col, next_col) + corridor_width // 2 + 1)):
                            if (r, c) not in preserve_nodes:
                                grid[r][c].color = EMPTY_COLOR
                    
                    carve_passage(next_row, next_col)
    
    # Start from top-left corner, using calculated step size
    start_row = 0
    start_col = 0
    carve_passage(start_row, start_col)
    
    # Ensure clear path from start to end areas (skip preserved nodes)
    for i in range(min(5, rows)):
        for j in range(min(5, cols)):
            if (i, j) not in preserve_nodes:
                grid[i][j].color = EMPTY_COLOR
    
    for i in range(max(0, rows-5), rows):
        for j in range(max(0, cols-5), cols):
            if (i, j) not in preserve_nodes:
                grid[i][j].color = EMPTY_COLOR


class Node:
    # Each cell in the grid
    def __init__(self, row, col, total_rows):
        self.row = row
        self.col = col
        self.color = EMPTY_COLOR
        self.neighbors = []
        self.total_rows = total_rows
        self.weight = 1
        self.g_score = float("inf")
        self.h_score = float("inf")
        self.f_score = float("inf")
    
    def get_pos(self):
        return self.row, self.col
    
    def is_closed(self):
        return self.color == RED
    
    def is_open(self):
        return self.color == GREEN
    
    def is_barrier(self):
        return self.color == BLACK

    def is_weight(self):
        return self.weight > 1 and not self.is_barrier() and not self.is_start() and not self.is_end()
    
    def is_start(self):
        return self.color == ORANGE
    
    def is_end(self):
        return self.color == PURPLE
    
    def reset(self):
        self.color = EMPTY_COLOR
        self.weight = 1
        self.g_score = float("inf")
        self.h_score = float("inf")
        self.f_score = float("inf")
    
    def make_start(self):
        self.color = ORANGE
        self.weight = 1
    
    def make_closed(self):
        self.color = RED
    
    def make_open(self):
        self.color = GREEN
    
    def make_barrier(self):
        self.color = BLACK
        self.weight = 1
    
    def make_end(self):
        self.color = PURPLE
        self.weight = 1
    
    def make_path(self):
        self.color = PATH_COLOR

    def make_weight(self, weight_value):
        self.weight = weight_value
        self.color = WEIGHT_COLOR
    
    def can_fit_robot(self, grid, robot_size):
        # Check if robot footprint fits here without hitting walls
        if robot_size == 1:
            return not self.is_barrier()
        
        # for bigger robots, check all cells they occupy
        for dr in range(robot_size):
            for dc in range(robot_size):
                check_row = self.row + dr
                check_col = self.col + dc
                
                # Boundary check - robot must fit completely within grid
                if check_row < 0 or check_row >= self.total_rows or check_col < 0 or check_col >= self.total_rows:
                    return False
                
                # Barrier check
                if grid[check_row][check_col].is_barrier():
                    return False
        
        return True
    
    def update_neighbors(self, grid, allow_diagonal=False, robot_size=1):
        # find all neighbors this node can move to
        self.neighbors = []
        
        # Down
        if self.row < self.total_rows - 1 and grid[self.row + 1][self.col].can_fit_robot(grid, robot_size):
            self.neighbors.append(grid[self.row + 1][self.col])
        
        # Up
        if self.row > 0 and grid[self.row - 1][self.col].can_fit_robot(grid, robot_size):
            self.neighbors.append(grid[self.row - 1][self.col])
        
        # Right
        if self.col < self.total_rows - 1 and grid[self.row][self.col + 1].can_fit_robot(grid, robot_size):
            self.neighbors.append(grid[self.row][self.col + 1])
        
        # Left
        if self.col > 0 and grid[self.row][self.col - 1].can_fit_robot(grid, robot_size):
            self.neighbors.append(grid[self.row][self.col - 1])
        
        if allow_diagonal:
            # Down-Right
            if (self.row < self.total_rows - 1 and self.col < self.total_rows - 1 and 
                grid[self.row + 1][self.col + 1].can_fit_robot(grid, robot_size)):
                self.neighbors.append(grid[self.row + 1][self.col + 1])
            
            # Down-Left
            if (self.row < self.total_rows - 1 and self.col > 0 and 
                grid[self.row + 1][self.col - 1].can_fit_robot(grid, robot_size)):
                self.neighbors.append(grid[self.row + 1][self.col - 1])
            
            # Up-Right
            if (self.row > 0 and self.col < self.total_rows - 1 and 
                grid[self.row - 1][self.col + 1].can_fit_robot(grid, robot_size)):
                self.neighbors.append(grid[self.row - 1][self.col + 1])
            
            # Up-Left
            if (self.row > 0 and self.col > 0 and 
                grid[self.row - 1][self.col - 1].can_fit_robot(grid, robot_size)):
                self.neighbors.append(grid[self.row - 1][self.col - 1])
    
    def __lt__(self, other):
        return False


def h(p1, p2):
    # manhattan distance heuristic for A*
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from, current, canvas, grid, robot_size=1):
    # trace back the path from goal to start
    path_nodes = []
    path_length = 0
    temp_current = current
    while temp_current in came_from:
        temp_current = came_from[temp_current]
        path_nodes.append(temp_current)
        # draw full robot footprint as path
        for dr in range(robot_size):
            for dc in range(robot_size):
                r = temp_current.row + dr
                c = temp_current.col + dc
                if 0 <= r < len(grid) and 0 <= c < len(grid[0]):
                    node = grid[r][c]
                    if not node.is_start() and not node.is_end() and not node.is_barrier():
                        # keep weighted terrain visible with darker shade
                        if node.is_weight():
                            node.color = "#149873"  # darker green
                        else:
                            node.make_path()
                        draw_node(canvas, node)
        canvas.update()
        path_length += 1
    
    # Reverse to get path from start to end
    path_nodes.reverse()
    return path_length, path_nodes


def algorithm(canvas, grid, start, end, allow_diagonal=False, robot_size=1,
              draw_callback=None, fog_of_war_enabled=False, fog_of_war_visible=None,
              fog_radius=0):
    # Main A* algorithm - returns metrics dict
    start_time = time.perf_counter()
    count = 0
    nodes_explored = 0
    open_heap = []
    heapq.heappush(open_heap, (0, count, start))
    came_from = {}

    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0

    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}
    start.g_score = 0
    start.h_score = f_score[start]
    start.f_score = f_score[start]
    closed_set = set()
    max_open_size = 1
    
    # count walkable cells for efficiency calculation
    total_walkable = sum(1 for row in grid for node in row if not node.is_barrier())

    def reveal_fog(center_node):
        if not fog_of_war_enabled or fog_of_war_visible is None:
            return

        if fog_radius and fog_radius > 0:
            for dr in range(-fog_radius, fog_radius + 1):
                for dc in range(-fog_radius, fog_radius + 1):
                    r = center_node.row + dr
                    c = center_node.col + dc
                    if 0 <= r < ROWS and 0 <= c < ROWS:
                        if abs(dr) + abs(dc) <= fog_radius:
                            fog_of_war_visible.add((r, c))
        else:
            for dr in range(robot_size):
                for dc in range(robot_size):
                    r = center_node.row + dr
                    c = center_node.col + dc
                    if 0 <= r < ROWS and 0 <= c < ROWS:
                        fog_of_war_visible.add((r, c))

    while open_heap:
        max_open_size = max(max_open_size, len(open_set_hash))
        current = heapq.heappop(open_heap)[2]
        # print(f"Current node: ({current.row}, {current.col})")  # debug
        if current not in open_set_hash:
            continue

        open_set_hash.remove(current)
        nodes_explored += 1
        # print(f"Nodes explored: {nodes_explored}")  # for testing
        closed_set.add(current)

        reveal_fog(current)
        if fog_of_war_enabled and draw_callback:
            draw_callback()
            canvas.update()

        # Check if goal is reached: either current node IS the goal, or robot footprint touches goal
        goal_reached = (current == end)  # For 1x1 robot
        
        # For multi-cell robots, check if ANY cell of robot footprint touches goal
        if not goal_reached and robot_size > 1:
            for dr in range(robot_size):
                for dc in range(robot_size):
                    r = current.row + dr
                    c = current.col + dc
                    if 0 <= r < len(grid) and 0 <= c < len(grid[0]):
                        # Compare position with goal position
                        if r == end.row and c == end.col:
                            goal_reached = True
                            break
                if goal_reached:
                    break

        if goal_reached:
            path_length, path_nodes = reconstruct_path(came_from, current, canvas, grid, robot_size=robot_size)
            end.make_end()
            start.make_start()
            if not fog_of_war_enabled:
                draw_node(canvas, end)
                draw_node(canvas, start)
            elapsed_time = time.perf_counter() - start_time
            
            # calculate search effectiveness - combines exploration, time, and path quality
            # this formula took forever to get right lol
            exploration_efficiency = ((total_walkable - nodes_explored) / total_walkable) if total_walkable > 0 else 0
            time_factor = max(0.5, min(1.0, 1.0 / (elapsed_time * 1000 + 1)))
            optimality = max(0.5, min(1.0, total_walkable / (nodes_explored + 1)))
            # print(f"Exploration: {exploration_efficiency}, Time: {time_factor}, Opt: {optimality}")  # debug
            search_effectiveness_score = (exploration_efficiency * 40 + time_factor * 30 + optimality * 30)

            metrics = {
                'success': True,
                'nodes_explored': nodes_explored,
                'path_length': path_length,
                'max_open_size': max_open_size,
                'time': elapsed_time,
                'space_complexity': len(closed_set),
                'search_efficiency': search_effectiveness_score,
                'exploration_efficiency': exploration_efficiency * 100,
                'path_nodes': path_nodes,
                'total_walkable': total_walkable
            }
            return metrics

        for neighbor in current.neighbors:
            # diagonal moves cost more (sqrt 2)
            is_diagonal = abs(neighbor.row - current.row) + abs(neighbor.col - current.col) == 2
            move_cost = math.sqrt(2) if is_diagonal else 1
            temp_g_score = g_score[current] + (move_cost * neighbor.weight)

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                neighbor.g_score = g_score[neighbor]
                neighbor.h_score = h(neighbor.get_pos(), end.get_pos())
                neighbor.f_score = f_score[neighbor]

                if neighbor not in open_set_hash:
                    count += 1
                    heapq.heappush(open_heap, (f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()
                    if not fog_of_war_enabled:
                        draw_node(canvas, neighbor)

        if not fog_of_war_enabled:
            canvas.update()

        if current != start:
            current.make_closed()
            if not fog_of_war_enabled:
                draw_node(canvas, current)

    elapsed_time = time.perf_counter() - start_time
    # if no path found, still calculate score
    exploration_efficiency = ((total_walkable - nodes_explored) / total_walkable) if total_walkable > 0 else 0
    time_factor = max(0.5, min(1.0, 1.0 / (elapsed_time * 1000 + 1)))
    search_effectiveness_score = (exploration_efficiency * 50 + time_factor * 50)
    metrics = {
        'success': False,
        'nodes_explored': nodes_explored,
        'path_length': 0,
        'max_open_size': max_open_size,
        'time': elapsed_time,
        'space_complexity': len(closed_set),
        'search_efficiency': search_effectiveness_score,
        'exploration_efficiency': exploration_efficiency * 100,
        'total_walkable': total_walkable
    }
    return metrics


def make_grid(rows):
    # make the grid with all the nodes
    grid = []
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, rows)
            grid[i].append(node)
    return grid


def draw_node(canvas, node):
    # draws individual node on canvas
    x = node.col * CELL_SIZE
    y = node.row * CELL_SIZE
    margin = 1
    
    # Skip drawing empty cells - let canvas background show through
    if node.color == EMPTY_COLOR:
        return
    
    # Draw with slight padding for better appearance
    if node.is_weight():
        # Draw weighted terrain with visible semi-transparent overlay
        # light base first
        canvas.create_rectangle(
            x + margin, y + margin,
            x + CELL_SIZE - margin, y + CELL_SIZE - margin,
            fill="#FFE6E6", outline="", tags="cell"
        )
        # Then overlay with semi-transparent red using stipple
        canvas.create_rectangle(
            x + margin, y + margin,
            x + CELL_SIZE - margin, y + CELL_SIZE - margin,
            fill=WEIGHT_COLOR, outline="", tags="cell", stipple="gray50"
        )
        # border for visibility
        canvas.create_rectangle(
            x + margin, y + margin,
            x + CELL_SIZE - margin, y + CELL_SIZE - margin,
            fill="", outline="#DC143C", width=1, tags="cell"
        )
    else:
        canvas.create_rectangle(
            x + margin, y + margin, 
            x + CELL_SIZE - margin, y + CELL_SIZE - margin,
            fill=node.color, outline="", tags="cell"
        )


def draw_node_with_image(canvas, node, obstacle_photo=None):
    # draws node but uses image for obstacles if we have one
    x = node.col * CELL_SIZE
    y = node.row * CELL_SIZE
    margin = 1
    
    # If it's a barrier and we have a custom obstacle image
    if node.is_barrier() and obstacle_photo:
        center_x = x + CELL_SIZE / 2
        center_y = y + CELL_SIZE / 2
        canvas.create_image(center_x, center_y, image=obstacle_photo, tags="cell")
    else:
        # Default drawing (including weights)
        draw_node(canvas, node)


def draw_robot(canvas, row, col, size, color):
    # simple robot drawing with body, head, eyes
    x = col * CELL_SIZE
    y = row * CELL_SIZE
    center_x = x + (size * CELL_SIZE) / 2
    center_y = y + (size * CELL_SIZE) / 2
    robot_size = min(CELL_SIZE * size * 0.7, 40)
    
    # Robot body (rounded rectangle)
    body_margin = robot_size * 0.15
    canvas.create_rectangle(
        center_x - robot_size/2, center_y - robot_size/2 + body_margin,
        center_x + robot_size/2, center_y + robot_size/2,
        fill=DARK_GREY, outline=color, width=2, tags="robot"
    )
    
    # Robot head (circle)
    head_radius = robot_size * 0.25
    canvas.create_oval(
        center_x - head_radius, center_y - robot_size/2 - head_radius,
        center_x + head_radius, center_y - robot_size/2 + head_radius,
        fill=color, outline=DARK_GREY, width=2, tags="robot"
    )
    
    # Eyes
    eye_size = robot_size * 0.08
    eye_y = center_y - robot_size/2 - head_radius * 0.3
    canvas.create_oval(
        center_x - head_radius * 0.4 - eye_size, eye_y - eye_size,
        center_x - head_radius * 0.4 + eye_size, eye_y + eye_size,
        fill=WHITE, outline="", tags="robot"
    )
    canvas.create_oval(
        center_x + head_radius * 0.4 - eye_size, eye_y - eye_size,
        center_x + head_radius * 0.4 + eye_size, eye_y + eye_size,
        fill=WHITE, outline="", tags="robot"
    )
    
    # Antenna
    antenna_height = robot_size * 0.15
    canvas.create_line(
        center_x, center_y - robot_size/2 - head_radius * 2,
        center_x, center_y - robot_size/2 - head_radius * 2 - antenna_height,
        fill=color, width=2, tags="robot"
    )
    canvas.create_oval(
        center_x - 3, center_y - robot_size/2 - head_radius * 2 - antenna_height - 3,
        center_x + 3, center_y - robot_size/2 - head_radius * 2 - antenna_height + 3,
        fill=color, outline="", tags="robot"
    )


def draw_flag(canvas, row, col, color):
    # goal flag
    x = col * CELL_SIZE + CELL_SIZE / 2
    y = row * CELL_SIZE + CELL_SIZE / 2
    flag_height = CELL_SIZE * 0.6
    
    # Pole
    canvas.create_line(x, y + flag_height/2, x, y - flag_height/2, fill=DARK_GREY, width=3, tags="robot")
    
    # Flag
    flag_width = CELL_SIZE * 0.4
    flag_points = [
        x, y - flag_height/2,
        x + flag_width, y - flag_height/4,
        x, y
    ]
    canvas.create_polygon(flag_points, fill=color, outline=DARK_GREY, width=2, tags="robot")


def draw_grid(canvas, theme_key="rabbit"):
    # redraws entire grid based on current theme
    theme = THEME_CONFIG.get(theme_key, THEME_CONFIG["rabbit"])
    canvas.delete("all")
    
    # Set canvas background to match theme
    canvas.config(bg=theme["canvas_bg"])
    
    # Background
    canvas.create_rectangle(0, 0, WIDTH, WIDTH, fill=theme["canvas_bg"], outline="")
    
    # Grid lines - subtle
    for i in range(ROWS + 1):
        pos = i * CELL_SIZE
        canvas.create_line(0, pos, WIDTH, pos, fill=theme["grid_line"], width=1)
        canvas.create_line(pos, 0, pos, WIDTH, fill=theme["grid_line"], width=1)


def draw_robot(canvas, row, col, size, color):
    """Draw a cute robot icon at the specified position"""
    x = col * CELL_SIZE
    y = row * CELL_SIZE
    center_x = x + (size * CELL_SIZE) / 2
    center_y = y + (size * CELL_SIZE) / 2
    robot_size = min(CELL_SIZE * size * 0.7, 40)
    
    # Robot body (rounded rectangle)
    body_margin = robot_size * 0.15
    canvas.create_rectangle(
        center_x - robot_size/2, center_y - robot_size/2 + body_margin,
        center_x + robot_size/2, center_y + robot_size/2,
        fill=DARK_GREY, outline=color, width=2, tags="robot"
    )
    
    # Robot head (circle)
    head_radius = robot_size * 0.25
    canvas.create_oval(
        center_x - head_radius, center_y - robot_size/2 - head_radius,
        center_x + head_radius, center_y - robot_size/2 + head_radius,
        fill=color, outline=DARK_GREY, width=2, tags="robot"
    )
    
    # Eyes
    eye_size = robot_size * 0.08
    eye_y = center_y - robot_size/2 - head_radius * 0.3
    canvas.create_oval(
        center_x - head_radius * 0.4 - eye_size, eye_y - eye_size,
        center_x - head_radius * 0.4 + eye_size, eye_y + eye_size,
        fill=WHITE, outline="", tags="robot"
    )
    canvas.create_oval(
        center_x + head_radius * 0.4 - eye_size, eye_y - eye_size,
        center_x + head_radius * 0.4 + eye_size, eye_y + eye_size,
        fill=WHITE, outline="", tags="robot"
    )
    
    # Antenna
    antenna_height = robot_size * 0.15
    canvas.create_line(
        center_x, center_y - robot_size/2 - head_radius * 2,
        center_x, center_y - robot_size/2 - head_radius * 2 - antenna_height,
        fill=color, width=2, tags="robot"
    )
    canvas.create_oval(
        center_x - 3, center_y - robot_size/2 - head_radius * 2 - antenna_height - 3,
        center_x + 3, center_y - robot_size/2 - head_radius * 2 - antenna_height + 3,
        fill=color, outline="", tags="robot"
    )


class AStar_App:
    def __init__(self, root):
        self.root = root
        self.root.title("A* Pathfinding - Path Planning with Random Obstacles")
        
        # Configure window with better geometry for full visibility
        optimal_width = WIDTH + 340 + 40
        optimal_height = WIDTH + 100
        self.root.geometry(f"{optimal_width}x{optimal_height}")
        self.root.minsize(1100, 900)  # Minimum size to ensure all elements visible
        self.root.configure(bg="#1a1a1a")
        
        # Initialize professional theme manager
        assets_path = Path(__file__).parent / "themes"
        self.theme_manager = ThemeManager(assets_path)
        self.current_theme_key = "rabbit"
        
        self.grid = make_grid(ROWS)
        self.start = None
        self.end = None
        self.allow_diagonal = False
        self.robot_size = 1
        self.running = False
        self.metrics_history = []
        self.paint_weight_var = tk.BooleanVar(value=False)
        self.ctrl_pressed = False  # Track Ctrl key state for terrain painting
        self.ghost_paths = []  # Store previous paths for comparison
        self.previous_run = None  # Store previous run metrics
        self.current_model_label = "Point Model"  # Track active model
        self.ghost_color = "#404040"  # Default ghost path color (updated per theme)
        
        # Custom images
        self.robot_image = None
        self.robot_photo = None
        self.obstacle_image = None
        self.obstacle_photo = None
        self.goal_image = None
        self.goal_photo = None
        self.use_custom_robot = False
        self.use_custom_obstacle = False
        self.use_custom_goal = False
        
        # Main container with grid layout
        main_container = ctk.CTkFrame(root, fg_color="#1a1a1a")
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=0)
        main_container.grid_rowconfigure(0, weight=1)
        
        # Left: Canvas area (responsive)
        canvas_container = ctk.CTkFrame(main_container, fg_color="#2b2b2b", corner_radius=15)
        canvas_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        self.canvas = tk.Canvas(canvas_container, width=WIDTH, height=WIDTH, 
                               bg=BACKGROUND_COLOR, highlightthickness=0, bd=0)
        self.canvas.pack(padx=15, pady=15)
        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        
        # Ctrl key tracking for high-cost terrain (Shift was causing issues)
        self.root.bind("<KeyPress-Control_L>", lambda e: self.set_ctrl(True))
        self.root.bind("<KeyPress-Control_R>", lambda e: self.set_ctrl(True))
        self.root.bind("<KeyRelease-Control_L>", lambda e: self.set_ctrl(False))
        self.root.bind("<KeyRelease-Control_R>", lambda e: self.set_ctrl(False))
        
        # Give canvas focus for event capture
        self.canvas.focus_set()
        self.canvas.bind("<FocusIn>", lambda e: None)  # Keep focus
        
        # Key bindings for theme switching
        self.root.bind("1", lambda e: self.switch_theme_by_key("rabbit"))
        self.root.bind("2", lambda e: self.switch_theme_by_key("space"))
        self.root.bind("3", lambda e: self.switch_theme_by_key("escape"))
        
        # Right: Modern side panel with CustomTkinter
        side_panel = ctk.CTkScrollableFrame(main_container, width=320, fg_color="#2b2b2b", corner_radius=15)
        side_panel.grid(row=0, column=1, sticky="ns")
        side_panel.grid_columnconfigure(0, weight=1)
        
        # Title with gradient effect
        title_frame = ctk.CTkFrame(side_panel, fg_color="transparent")
        title_frame.pack(pady=(10, 5), padx=15, fill=tk.X)
        
        ctk.CTkLabel(title_frame, text="Path Planning A*", 
                    font=ctk.CTkFont(size=20, weight="bold"),
                    text_color="#00d4ff").pack()
        
        # Theme info with modern card
        self.theme_info_label = ctk.CTkLabel(side_panel, text="", 
                                            font=ctk.CTkFont(size=11),
                                            text_color="#a0a0a0",
                                            justify="left",
                                            wraplength=280)
        self.theme_info_label.pack(pady=(0, 15), padx=15)
        
        # Robot Settings
        robot_frame = ctk.CTkFrame(side_panel, fg_color="#1e1e1e", corner_radius=10)
        robot_frame.pack(pady=10, padx=15, fill=tk.X)

        ctk.CTkLabel(robot_frame, text="Movement Model", 
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#00d4ff").pack(pady=(10, 5), padx=10, anchor="w")

        self.robot_label = ctk.CTkLabel(robot_frame, text=f"Model Size: {self.robot_size}×{self.robot_size}",
                                       font=ctk.CTkFont(size=10),
                                       text_color="#e0e0e0")
        self.robot_label.pack(pady=(5, 2), padx=10, anchor="w")

        btn_frame1 = ctk.CTkFrame(robot_frame, fg_color="transparent")
        btn_frame1.pack(pady=(0, 10), padx=10)
        ctk.CTkButton(btn_frame1, text="1×1", width=70, height=32,
                     command=lambda: self.set_robot_size(1),
                     fg_color="#444", hover_color="#666", corner_radius=8,
                     font=ctk.CTkFont(size=11, weight="bold")).pack(side=tk.LEFT, padx=3)
        ctk.CTkButton(btn_frame1, text="2×2", width=70, height=32,
                     command=lambda: self.set_robot_size(2),
                     fg_color="#444", hover_color="#666", corner_radius=8,
                     font=ctk.CTkFont(size=11, weight="bold")).pack(side=tk.LEFT, padx=3)
        ctk.CTkButton(btn_frame1, text="3×3", width=70, height=32,
                     command=lambda: self.set_robot_size(3),
                     fg_color="#444", hover_color="#666", corner_radius=8,
                     font=ctk.CTkFont(size=11, weight="bold")).pack(side=tk.LEFT, padx=3)

        # Environment (Themes + Maze/Random)
        environment_frame = ctk.CTkFrame(side_panel, fg_color="#1e1e1e", corner_radius=10)
        environment_frame.pack(pady=10, padx=15, fill=tk.X)

        ctk.CTkLabel(environment_frame, text="Environment", 
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#00d4ff").pack(pady=(10, 5), padx=10, anchor="w")

        ctk.CTkLabel(environment_frame, text="Themes (Press 1/2/3):", 
                    font=ctk.CTkFont(size=10),
                    text_color="#e0e0e0").pack(pady=(5, 2), padx=10, anchor="w")

        themes = [
            ("rabbit", "1 Carrot Hunt", "#27ae60"),
            ("space", "2 Space", "#3498db"),
            ("escape", "3 Dungeon", "#e74c3c")
        ]

        for theme_key, text, color in themes:
            ctk.CTkButton(environment_frame, text=text, height=38,
                         command=lambda t=theme_key: self.switch_theme_by_key(t),
                         fg_color=color, hover_color="#555", corner_radius=8,
                         font=ctk.CTkFont(size=11, weight="bold")).pack(pady=4, padx=10, fill=tk.X)

        ctk.CTkLabel(environment_frame, text="Density (Random Mode):", 
                    font=ctk.CTkFont(size=10),
                    text_color="#e0e0e0").pack(pady=(8, 2), padx=10, anchor="w")

        self.density_var = tk.IntVar(value=15)
        ctk.CTkSlider(environment_frame, from_=5, to=40, number_of_steps=35, width=260,
                     variable=self.density_var,
                     button_color="#00d4ff", button_hover_color="#00a8cc",
                     progress_color="#00d4ff", fg_color="#444").pack(pady=(0, 10), padx=10)

        button_row = ctk.CTkFrame(environment_frame, fg_color="transparent")
        button_row.pack(padx=10, fill=tk.X, pady=(0, 10))

        ctk.CTkButton(button_row, text="Random", height=35, width=130,
                     command=self.generate_obstacles,
                     fg_color="#E67E22", hover_color="#d35400", corner_radius=8,
                     font=ctk.CTkFont(size=10, weight="bold")).pack(side=tk.LEFT, padx=3)

        ctk.CTkButton(button_row, text="Maze", height=35, width=130,
                     command=self.generate_maze_structure,
                     fg_color="#9B59B6", hover_color="#8E44AD", corner_radius=8,
                     font=ctk.CTkFont(size=10, weight="bold")).pack(side=tk.LEFT, padx=3)

        # Random weights button
        button_row2 = ctk.CTkFrame(environment_frame, fg_color="transparent")
        button_row2.pack(padx=10, fill=tk.X, pady=(5, 10))
        ctk.CTkButton(button_row2, text="Random Weights", height=35, width=270,
                     command=self.generate_random_weights,
                     fg_color="#c44569", hover_color="#e55983", corner_radius=8,
                     font=ctk.CTkFont(size=10, weight="bold")).pack()

        # Visual Effects
        visual_frame = ctk.CTkFrame(side_panel, fg_color="#1e1e1e", corner_radius=10)
        visual_frame.pack(pady=10, padx=15, fill=tk.X)

        ctk.CTkLabel(visual_frame, text="Terrain Tools", 
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#00d4ff").pack(pady=(10, 5), padx=10, anchor="w")
        
        brush_checkbox = ctk.CTkCheckBox(visual_frame, text="High-Cost Terrain Brush", 
                                         variable=self.paint_weight_var,
                                         onvalue=True, offvalue=False,
                                         font=ctk.CTkFont(size=10))
        brush_checkbox.pack(padx=10, pady=(0, 6), anchor="w")

        # Tip label for Ctrl+Drag
        tip_label = ctk.CTkLabel(visual_frame, text="Tip: Hold Ctrl + Drag to add weighted terrain",
                                 font=ctk.CTkFont(size=9),
                                 text_color="#6c757d")
        tip_label.pack(padx=10, pady=(0, 6), anchor="w")

        self.weight_info_label = ctk.CTkLabel(visual_frame, text=f"Cost: {WEIGHT_VALUE}×", 
                                              font=ctk.CTkFont(size=10),
                                              text_color="#a0a0a0")
        self.weight_info_label.pack(pady=(0, 10), padx=10, anchor="w")
        
        # Algorithm Controls
        algo_frame = ctk.CTkFrame(side_panel, fg_color="#1e1e1e", corner_radius=10)
        algo_frame.pack(pady=10, padx=15, fill=tk.X)
        
        ctk.CTkLabel(algo_frame, text="Pathfinding Algorithms", 
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#00d4ff").pack(pady=(10, 5), padx=10, anchor="w")
        
        ctk.CTkButton(algo_frame, text="A* (4-directions)", height=35,
                     command=lambda: self.run_algorithm(diagonal=False),
                     fg_color="#2ECC71", hover_color="#27ae60", corner_radius=8,
                     font=ctk.CTkFont(size=11, weight="bold")).pack(pady=3, padx=10, fill=tk.X)
        
        ctk.CTkButton(algo_frame, text="A* (Diagonal)", height=35,
                     command=lambda: self.run_algorithm(diagonal=True),
                     fg_color="#1ABC9C", hover_color="#16a085", corner_radius=8,
                     font=ctk.CTkFont(size=11, weight="bold")).pack(pady=3, padx=10, fill=tk.X)
        
        ctk.CTkButton(algo_frame, text="Clear Grid", height=35,
                     command=self.clear_grid,
                     fg_color="#E74C3C", hover_color="#c0392b", corner_radius=8,
                     font=ctk.CTkFont(size=11, weight="bold")).pack(pady=(3, 10), padx=10, fill=tk.X)
        
        # Performance Metrics
        metrics_frame = ctk.CTkFrame(side_panel, fg_color="#1e1e1e", corner_radius=10)
        metrics_frame.pack(pady=10, padx=15, fill=tk.X)
        
        ctk.CTkLabel(metrics_frame, text="Performance Metrics", 
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#00d4ff").pack(pady=(10, 5), padx=10, anchor="w")
        
        self.metrics_text = ctk.CTkTextbox(metrics_frame, height=90, wrap=tk.WORD,
                                          fg_color="#2b2b2b", text_color="#00ff88",
                                          font=ctk.CTkFont(family="Courier", size=10),
                                          corner_radius=8, activate_scrollbars=False)
        self.metrics_text.pack(pady=(0, 10), padx=10, fill=tk.X)
        self.update_metrics_display()

        self.node_info_label = ctk.CTkLabel(metrics_frame, text="Hover over nodes → g=cost from start, h=est. to goal, f=g+h, w=weight",
                            font=ctk.CTkFont(size=9),
                            text_color="#a0a0a0")
        self.node_info_label.pack(pady=(0, 10), padx=10, anchor="w")
        
        # Instructions
        # Comparison Table
        compare_frame = ctk.CTkFrame(side_panel, fg_color="#1e1e1e", corner_radius=10)
        compare_frame.pack(pady=10, padx=15, fill=tk.X)
        
        ctk.CTkLabel(compare_frame, text="Model Comparison - ADS Metrics", 
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#00d4ff").pack(pady=(10, 5), padx=10, anchor="w")
        
        # Create actual table with grid layout
        self.comparison_table_frame = ctk.CTkFrame(compare_frame, fg_color="#2b2b2b", corner_radius=8, height=180)
        self.comparison_table_frame.pack(pady=(0, 10), padx=10, fill=tk.X)
        self.comparison_table_frame.pack_propagate(False)  # Maintain height
        
        # Initialize empty table cells (will be populated by update_comparison_table)
        self.table_cells = {}
        
        instr_frame = ctk.CTkFrame(side_panel, fg_color="#1e1e1e", corner_radius=10)
        instr_frame.pack(pady=10, padx=15, fill=tk.BOTH, expand=True)
        
        ctk.CTkLabel(instr_frame, text="Instructions", 
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#00d4ff").pack(pady=(10, 5), padx=10, anchor="w")
        
        instructions = ctk.CTkTextbox(instr_frame, height=120, wrap=tk.WORD,
                                     fg_color="#2b2b2b", text_color="#e0e0e0",
                                     font=ctk.CTkFont(size=10), corner_radius=8,
                                     activate_scrollbars=True)
        instructions.pack(pady=(0, 10), padx=10, fill=tk.BOTH, expand=True)
        instructions.insert("1.0", "• Left-click: Place start → end → obstacle\n• Right-click: Erase cell\n• Drag: Draw obstacles\n• Enable High-Cost Terrain Brush: Add weighted cells\n• Ctrl+Drag: Quick weighted terrain (always available)\n• Set robot size before planning\n• Generate Random/Maze for obstacles")
        instructions.configure(state="disabled")
        
        self.redraw()
        self.draw_robot_outline()
    
    def draw_robot_outline(self):
        """Draw robot footprint outline and robot icon at start position"""
        if self.start:
            # Draw footprint outline
            if self.robot_size > 1:
                x = self.start.col * CELL_SIZE
                y = self.start.row * CELL_SIZE
                w = self.robot_size * CELL_SIZE
                self.canvas.create_rectangle(x, y, x + w, y + w, outline=ORANGE, width=3, dash=(5, 3), tags="robot")
            
            # Draw robot (custom image or default)
            if self.use_custom_robot and self.robot_photo:
                x = self.start.col * CELL_SIZE
                y = self.start.row * CELL_SIZE
                center_x = x + (self.robot_size * CELL_SIZE) / 2
                center_y = y + (self.robot_size * CELL_SIZE) / 2
                self.canvas.create_image(center_x, center_y, image=self.robot_photo, tags="robot")
            else:
                draw_robot(self.canvas, self.start.row, self.start.col, self.robot_size, ORANGE)
        
        # Draw goal (custom image or default flag)
        # ALWAYS show goal - required for A* heuristic calculation
        if self.end:
            if self.use_custom_goal and self.goal_photo:
                x = self.end.col * CELL_SIZE
                y = self.end.row * CELL_SIZE
                center_x = x + CELL_SIZE / 2
                center_y = y + CELL_SIZE / 2
                self.canvas.create_image(center_x, center_y, image=self.goal_photo, tags="goal")
            else:
                draw_flag(self.canvas, self.end.row, self.end.col, PURPLE)
    
    def set_ctrl(self, pressed):
        """Track Ctrl key state"""
        self.ctrl_pressed = pressed
    
    def update_metrics_display(self, metrics=None):
        """Update the metrics display with ADS complexity measures"""
        self.metrics_text.configure(state="normal")
        self.metrics_text.delete("1.0", tk.END)
        
        if metrics:
            status = "SUCCESS" if metrics['success'] else "NO PATH FOUND"
            self.metrics_text.insert(tk.END, f"Status: {status}\n")
            self.metrics_text.insert(tk.END, f"Nodes Explored: {metrics['nodes_explored']}\n")
            self.metrics_text.insert(tk.END, f"Path Length: {metrics['path_length']:.2f}\n")
            self.metrics_text.insert(tk.END, f"Peak Priority Queue: {metrics['max_open_size']}\n")
            self.metrics_text.insert(tk.END, f"Time Complexity: {metrics['time']*1000:.2f} ms\n")
            self.metrics_text.insert(tk.END, f"Space Complexity: {metrics.get('space_complexity', 0)} nodes\n")
            # Display composite search effectiveness score
            score = metrics.get('search_efficiency', 0)
            raw_eff = metrics.get('exploration_efficiency', 0)
            self.metrics_text.insert(tk.END, f"Search Effectiveness: {score:.1f}/100\n")
            self.metrics_text.insert(tk.END, f"  └─ Exploration Efficiency: {raw_eff:.1f}%\n")
            self.metrics_text.insert(tk.END, f"\nRobot: {self.robot_size}x{self.robot_size}\n")
            self.metrics_text.insert(tk.END, f"Diagonal: {'Yes' if self.allow_diagonal else 'No'}")
        else:
            self.metrics_text.insert(tk.END, "Run algorithm to see metrics...")
        
        self.metrics_text.configure(state="disabled")
    
    def redraw(self):
        # Clear canvas to prevent memory leaks
        self.canvas.delete('all')
        
        draw_grid(self.canvas, self.current_theme_key)
        
        for row in self.grid:
            for node in row:
                # Skip drawing color for start/end nodes - let images show
                if node.is_start() or node.is_end():
                    continue
                
                if self.use_custom_obstacle and self.obstacle_photo:
                    draw_node_with_image(self.canvas, node, self.obstacle_photo)
                else:
                    draw_node(self.canvas, node)
        self.draw_robot_outline()
    
    def on_drag(self, event):
        """Handle dragging to draw barriers or weights"""
        if self.running:
            return
        
        row = event.y // CELL_SIZE
        col = event.x // CELL_SIZE
        
        if 0 <= row < ROWS and 0 <= col < ROWS:
            node = self.grid[row][col]
            # Only paint on cells that aren't start/end
            if node != self.start and node != self.end:
                # Paint weights if brush enabled OR (Ctrl is held AND start/end are already placed)
                if self.paint_weight_var.get() or (self.ctrl_pressed and self.start and self.end):
                    node.make_weight(WEIGHT_VALUE)
                else:
                    node.make_barrier()
                draw_node(self.canvas, node)
    
    def on_left_click(self, event):
        if self.running:
            return
        
        row = event.y // CELL_SIZE
        col = event.x // CELL_SIZE
        
        if 0 <= row < ROWS and 0 <= col < ROWS:
            node = self.grid[row][col]
            
            # PRIORITY 1: Always place start first
            if not self.start and node != self.end:
                self.start = node
                self.start.make_start()
            # PRIORITY 2: Always place end second
            elif not self.end and node != self.start:
                self.end = node
                self.end.make_end()
            # PRIORITY 3: After start & end placed - check what to paint
            elif node != self.end and node != self.start:
                # If Ctrl held OR brush enabled = paint weights
                if self.ctrl_pressed or self.paint_weight_var.get():
                    node.make_weight(WEIGHT_VALUE)
                # Otherwise = paint barriers
                else:
                    node.make_barrier()
            
            self.redraw()
    
    def on_right_click(self, event):
        if self.running:
            return
        
        row = event.y // CELL_SIZE
        col = event.x // CELL_SIZE
        
        if 0 <= row < ROWS and 0 <= col < ROWS:
            node = self.grid[row][col]
            node.reset()
            
            if node == self.start:
                self.start = None
            elif node == self.end:
                self.end = None
            
            self.redraw()

    def on_mouse_move(self, event):
        row = event.y // CELL_SIZE
        col = event.x // CELL_SIZE
        if 0 <= row < ROWS and 0 <= col < ROWS:
            node = self.grid[row][col]
            if node.is_barrier():
                self.node_info_label.configure(text="■ Barrier")
            elif node.is_start():
                self.node_info_label.configure(text="● Start Position")
            elif node.is_end():
                self.node_info_label.configure(text="◆ Goal Position")
            else:
                g_val = "—" if node.g_score == float("inf") else f"{node.g_score:.1f}"
                h_val = "—" if node.h_score == float("inf") else f"{node.h_score:.1f}"
                f_val = "—" if node.f_score == float("inf") else f"{node.f_score:.1f}"
                weight_marker = f" [WEIGHTED ×{node.weight}]" if node.is_weight() else ""
                self.node_info_label.configure(
                    text=f"g={g_val}  h={h_val}  f={f_val}  w={node.weight}{weight_marker}"
                )
    
    def update_comparison_table(self, current_result):
        """Update the model comparison table with actual GUI table"""
        # Clear existing table
        for widget in self.comparison_table_frame.winfo_children():
            widget.destroy()
        
        if self.previous_run:
            prev_model = self.previous_run.get('model', 'Previous')
            curr_model = self.current_model_label
            
            # Extract metrics
            prev_path = self.previous_run['path_length']
            curr_path = current_result['path_length']
            prev_nodes = self.previous_run['nodes_explored']
            curr_nodes = current_result['nodes_explored']
            prev_time = self.previous_run['time'] * 1000
            curr_time = current_result['time'] * 1000
            prev_space = self.previous_run.get('space_complexity', 0)
            curr_space = current_result.get('space_complexity', 0)
            prev_peak = self.previous_run.get('max_open_size', 0)
            curr_peak = current_result.get('max_open_size', 0)
            prev_eff = self.previous_run.get('search_efficiency', 0)
            curr_eff = current_result.get('search_efficiency', 0)
            
            # Calculate percentage differences
            path_diff = ((curr_path - prev_path) / prev_path * 100) if prev_path > 0 else 0
            nodes_diff = ((curr_nodes - prev_nodes) / prev_nodes * 100) if prev_nodes > 0 else 0
            time_diff = ((curr_time - prev_time) / prev_time * 100) if prev_time > 0 else 0
            space_diff = ((curr_space - prev_space) / prev_space * 100) if prev_space > 0 else 0
            peak_diff = ((curr_peak - prev_peak) / prev_peak * 100) if prev_peak > 0 else 0
            eff_diff = ((curr_eff - prev_eff) / prev_eff * 100) if prev_eff > 0 else 0
            
            # Helper to get indicator and color
            def get_indicator_color(diff, higher_is_better=False):
                threshold = 5
                if abs(diff) < threshold:
                    return "≈", "#808080"  # Grey for similar
                elif diff > 0:
                    if higher_is_better:
                        return "↑", "#44ff44"  # Green for better (increased efficiency)
                    else:
                        return "↑", "#ff4444"  # Red for worse (increased cost)
                else:
                    if higher_is_better:
                        return "↓", "#ff4444"  # Red for worse (decreased efficiency)
                    else:
                        return "↓", "#44ff44"  # Green for better (decreased cost)
            
            path_ind, path_color = get_indicator_color(path_diff)
            nodes_ind, nodes_color = get_indicator_color(nodes_diff)
            time_ind, time_color = get_indicator_color(time_diff)
            space_ind, space_color = get_indicator_color(space_diff)
            peak_ind, peak_color = get_indicator_color(peak_diff)
            eff_ind, eff_color = get_indicator_color(eff_diff, higher_is_better=True)  # Higher efficiency is better!
            
            # Create table with grid
            # Header row
            headers = ["Metric", "Previous", "Current", "Δ"]
            for col, header in enumerate(headers):
                label = ctk.CTkLabel(self.comparison_table_frame, text=header,
                                    font=ctk.CTkFont(size=10, weight="bold"),
                                    fg_color="#3a3a3a", text_color="#00d4ff",
                                    corner_radius=0, anchor="center")
                label.grid(row=0, column=col, sticky="nsew", padx=1, pady=1, ipadx=5, ipady=5)
            
            # Data rows
            rows = [
                ("Model", prev_model[:12], curr_model[:12], ""),
                ("Path", f"{prev_path:.1f}", f"{curr_path:.1f}", f"{path_ind} {abs(path_diff):.0f}%"),
                ("Nodes", f"{prev_nodes}", f"{curr_nodes}", f"{nodes_ind} {abs(nodes_diff):.0f}%"),
                ("Time(ms)", f"{prev_time:.1f}", f"{curr_time:.1f}", f"{time_ind} {abs(time_diff):.0f}%"),
                ("Peak PQ", f"{prev_peak}", f"{curr_peak}", f"{peak_ind} {abs(peak_diff):.0f}%"),
                ("Space", f"{prev_space}", f"{curr_space}", f"{space_ind} {abs(space_diff):.0f}%"),
                ("Effectiveness", f"{prev_eff:.1f}", f"{curr_eff:.1f}", f"{eff_ind} {abs(eff_diff):.1f}")
            ]
            
            row_colors = ["#2b2b2b", "#333333"]  # Alternating row colors
            delta_colors = ["", path_color, nodes_color, time_color, peak_color, space_color, eff_color]
            
            for row_idx, (metric, prev_val, curr_val, delta) in enumerate(rows):
                bg_color = row_colors[row_idx % 2]
                
                # Metric name
                label = ctk.CTkLabel(self.comparison_table_frame, text=metric,
                                    font=ctk.CTkFont(size=9),
                                    fg_color=bg_color, text_color="#e0e0e0",
                                    corner_radius=0, anchor="w")
                label.grid(row=row_idx+1, column=0, sticky="nsew", padx=1, pady=1, ipadx=5, ipady=3)
                
                # Previous value
                label = ctk.CTkLabel(self.comparison_table_frame, text=prev_val,
                                    font=ctk.CTkFont(size=9),
                                    fg_color=bg_color, text_color="#ffaa00",
                                    corner_radius=0, anchor="center")
                label.grid(row=row_idx+1, column=1, sticky="nsew", padx=1, pady=1, ipadx=5, ipady=3)
                
                # Current value
                label = ctk.CTkLabel(self.comparison_table_frame, text=curr_val,
                                    font=ctk.CTkFont(size=9),
                                    fg_color=bg_color, text_color="#ffaa00",
                                    corner_radius=0, anchor="center")
                label.grid(row=row_idx+1, column=2, sticky="nsew", padx=1, pady=1, ipadx=5, ipady=3)
                
                # Delta with color
                delta_color = delta_colors[row_idx] if row_idx > 0 else "#e0e0e0"
                label = ctk.CTkLabel(self.comparison_table_frame, text=delta,
                                    font=ctk.CTkFont(size=9, weight="bold"),
                                    fg_color=bg_color, text_color=delta_color,
                                    corner_radius=0, anchor="center")
                label.grid(row=row_idx+1, column=3, sticky="nsew", padx=1, pady=1, ipadx=5, ipady=3)
            
            # Legend
            legend = ctk.CTkLabel(self.comparison_table_frame, 
                                 text="↓=Better(less cost)  ↑=Worse(more cost)  ≈=Similar  |  Efficiency: ↑=Better",
                                 font=ctk.CTkFont(size=8),
                                 fg_color="#2b2b2b", text_color="#808080",
                                 corner_radius=0, anchor="center")
            legend.grid(row=8, column=0, columnspan=4, sticky="ew", padx=1, pady=(1, 5))
            
            # Configure grid weights
            for col in range(4):
                self.comparison_table_frame.grid_columnconfigure(col, weight=1)
        
        else:
            # First run - show message
            msg = ctk.CTkLabel(self.comparison_table_frame,
                              text=f"First Run: {self.current_model_label}\n\nRun another robot size\nto compare performance!",
                              font=ctk.CTkFont(size=10),
                              fg_color="#2b2b2b", text_color="#00d4ff",
                              justify="center")
            msg.pack(padx=10, pady=20)
        
        # Store current model in result
        current_result['model'] = self.current_model_label
    
    def set_robot_size(self, size):
        """Set robot size explicitly"""
        self.robot_size = size
        if size == 1:
            self.current_model_label = "Point Model (1x1)"
        elif size == 2:
            self.current_model_label = "Square Robot (2x2)"
        elif size == 3:
            self.current_model_label = "Square Robot (3x3)"
        else:
            self.current_model_label = f"Model {size}x{size}"
        self.robot_label.configure(text=f"Model Size: {self.robot_size}×{self.robot_size}")
        
        # Update theme info label to reflect new robot size
        theme = self.theme_manager.get_theme(self.current_theme_key)
        if theme:
            info_text = f"{theme.name}\n{theme.description}\nModel: {self.robot_size}×{self.robot_size} | Weight: {theme.weight_value}×"
            self.theme_info_label.configure(text=info_text)
        
        # Resize robot image if using custom theme
        if self.use_custom_robot and self.robot_image:
            new_size = int(CELL_SIZE * self.robot_size * 0.8)
            resized_img = self.robot_image.resize((new_size, new_size), Image.Resampling.LANCZOS)
            self.robot_photo = ImageTk.PhotoImage(resized_img)

        # Resize goal image to match robot size
        if self.use_custom_goal and self.goal_image:
            goal_size = int(CELL_SIZE * self.robot_size * 0.8)
            resized_goal = self.goal_image.resize((goal_size, goal_size), Image.Resampling.LANCZOS)
            self.goal_photo = ImageTk.PhotoImage(resized_goal)
        
        self.redraw()
    
    def generate_obstacles(self):
        """Generate random obstacles on the grid, ensuring a path remains possible"""
        if not self.start or not self.end:
            print("Please set start and end points first!")
            return

        protected = set()
        for dr in range(self.robot_size):
            for dc in range(self.robot_size):
                sr = self.start.row + dr
                sc = self.start.col + dc
                er = self.end.row + dr
                ec = self.end.col + dc
                if 0 <= sr < ROWS and 0 <= sc < ROWS:
                    protected.add((sr, sc))
                if 0 <= er < ROWS and 0 <= ec < ROWS:
                    protected.add((er, ec))
        
        density = self.density_var.get()
        max_attempts = 5
        path_found = False
        current_density = density
        
        for attempt in range(max_attempts):
            # Reset grid
            for row in self.grid:
                for node in row:
                    if (node.row, node.col) in protected:
                        if node != self.start and node != self.end:
                            node.reset()
                        continue
                    if node != self.start and node != self.end:
                        if random.randint(1, 100) <= current_density:
                            node.make_barrier()
                        else:
                            node.reset()
            
            # Update neighbors
            for row in self.grid:
                for node in row:
                    node.update_neighbors(self.grid, allow_diagonal=self.allow_diagonal, robot_size=self.robot_size)
            
            # Check if path is possible using a simple BFS
            from collections import deque
            visited = set()
            queue = deque([self.start])
            visited.add(self.start)
            
            while queue:
                current = queue.popleft()
                if current == self.end:
                    path_found = True
                    break
                for neighbor in current.neighbors:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
            
            if path_found:
                print(f"✓ Generated obstacles (density: {current_density}%) - path is possible")
                break
            else:
                # Reduce density and try again
                current_density = max(5, current_density - 10)
                print(f"Path blocked at {density}%, reducing to {current_density}%...")
        
        if not path_found:
            print("⚠ Warning: No path possible even at minimal density. Please adjust obstacles manually.")
        
        self.redraw()
    
    def generate_maze_structure(self):
        """Generate a perfect maze using recursive backtracking with robot-aware corridors"""
        if not self.start or not self.end:
            print("Please set start and end points first!")
            return
        
        print(f"Generating maze with {self.robot_size}×{self.robot_size} robot footprint...")
        
        # Preserve start and end positions with FULL robot footprint (no extra buffer)
        preserve = set()
        
        # Add start position and its full footprint (force clear to ensure open space)
        for dr in range(self.robot_size):
            for dc in range(self.robot_size):
                r = self.start.row + dr
                c = self.start.col + dc
                if 0 <= r < ROWS and 0 <= c < ROWS:
                    preserve.add((r, c))
                    self.grid[r][c].color = EMPTY_COLOR
        
        # Add end position and its full footprint (force clear to ensure open space)
        for dr in range(self.robot_size):
            for dc in range(self.robot_size):
                r = self.end.row + dr
                c = self.end.col + dc
                if 0 <= r < ROWS and 0 <= c < ROWS:
                    preserve.add((r, c))
                    self.grid[r][c].color = EMPTY_COLOR
        # Add end position and its full footprint
        for dr in range(self.robot_size):
            for dc in range(self.robot_size):
                r = self.end.row + dr
                c = self.end.col + dc
                if 0 <= r < ROWS and 0 <= c < ROWS:
                    preserve.add((r, c))
        
        # Generate the maze structure (will skip preserved positions)
        generate_maze(self.grid, robot_size=self.robot_size, preserve_nodes=preserve)
        
        # Force carve a guaranteed path from start to end (fallback connectivity)
        from collections import deque
        start_pos = (self.start.row, self.start.col)
        end_pos = (self.end.row, self.end.col)
        
        # Simple path carving: straight line with corridors
        if start_pos[0] <= end_pos[0]:
            for r in range(start_pos[0], end_pos[0] + 1):
                for c in range(max(0, start_pos[1] - 1), min(ROWS, start_pos[1] + self.robot_size + 1)):
                    self.grid[r][c].color = EMPTY_COLOR
        else:
            for r in range(end_pos[0], start_pos[0] + 1):
                for c in range(max(0, start_pos[1] - 1), min(ROWS, start_pos[1] + self.robot_size + 1)):
                    self.grid[r][c].color = EMPTY_COLOR
        
        if start_pos[1] <= end_pos[1]:
            for c in range(start_pos[1], end_pos[1] + 1):
                for r in range(max(0, start_pos[0] - 1), min(ROWS, start_pos[0] + self.robot_size + 1)):
                    self.grid[r][c].color = EMPTY_COLOR
        else:
            for c in range(end_pos[1], start_pos[1] + 1):
                for r in range(max(0, start_pos[0] - 1), min(ROWS, start_pos[0] + self.robot_size + 1)):
                    self.grid[r][c].color = EMPTY_COLOR
        
        # Update all neighbors for pathfinding
        for row in self.grid:
            for node in row:
                node.update_neighbors(self.grid, allow_diagonal=self.allow_diagonal, robot_size=self.robot_size)
        
        print(f"Maze generated - corridors sized for {self.robot_size}×{self.robot_size} robot")
        self.redraw()
    
    def generate_random_weights(self):
        """Add random weighted terrain (high-cost areas) to the grid"""
        if not self.start or not self.end:
            print("Please set start and end points first!")
            return
        
        print(f"Generating random weighted terrain...")
        
        # Add weighted cells to 10-20% of empty cells
        import random
        weight_density = random.randint(10, 20)
        
        empty_cells = []
        for row in self.grid:
            for node in row:
                # Only consider truly empty cells (not start, end, barriers, or already weighted)
                if (node != self.start and node != self.end and 
                    not node.is_barrier() and not node.is_weight()):
                    empty_cells.append(node)
        
        if empty_cells:
            num_weights = int(len(empty_cells) * weight_density / 100)
            weight_cells = random.sample(empty_cells, min(num_weights, len(empty_cells)))
            
            for node in weight_cells:
                node.make_weight(WEIGHT_VALUE)
            
            print(f"Added {len(weight_cells)} weighted terrain cells ({weight_density}% density)")
        else:
            print("No empty cells available for weighted terrain")
        
        self.redraw()
    
    def animate_robot_on_path(self, path_nodes):
        """Animate the robot moving along the found path"""
        if not path_nodes or not self.use_custom_robot or not self.robot_photo:
            return
        
        # Hide the start node during animation (only 1 rabbit on grid)
        if self.start:
            self.start.color = EMPTY_COLOR
        
        self.animation_index = 0
        self.path_nodes = path_nodes
        self._animate_robot_step()
    
    def _animate_robot_step(self):
        """Move robot one step along the path"""
        if not hasattr(self, 'animation_index') or not hasattr(self, 'path_nodes'):
            return
        
        if self.animation_index >= len(self.path_nodes):
            # Animation complete - restore the start node
            print("Robot animation complete!")
            if self.start:
                self.start.make_start()
            self.redraw()
            return
        
        # Get current path node
        node = self.path_nodes[self.animation_index]
        
        # Redraw the grid
        self.redraw()
        
        # Draw robot at this position
        if self.robot_photo:
            x = node.col * CELL_SIZE
            y = node.row * CELL_SIZE
            center_x = x + (self.robot_size * CELL_SIZE) / 2
            center_y = y + (self.robot_size * CELL_SIZE) / 2
            self.canvas.create_image(center_x, center_y, image=self.robot_photo, tags="robot")
        
        self.animation_index += 1
        
        # Schedule next step (150ms delay per step)
        self.root.after(150, self._animate_robot_step)
    
    def run_algorithm(self, diagonal=False):
        if not self.start or not self.end or self.running:
            return
        
        self.running = True
        self.allow_diagonal = diagonal
        
        # Convert previous path to ghost grey (do NOT clear it)
        if hasattr(self, 'ghost_paths'):
            for row in self.grid:
                for node in row:
                    if node.color == PATH_COLOR:
                        node.color = self.ghost_color  # Theme-appropriate ghost color
        
        # Clear exploration visualization but keep ghost paths
        for row in self.grid:
            for node in row:
                # Keep ghost paths (grey), clear only red/green exploration colors
                if node.color in [RED, GREEN] and not node.is_barrier() and not node.is_start() and not node.is_end() and not node.is_weight():
                    node.reset()
                elif node.color == self.ghost_color:  # Keep ghost paths (theme-aware)
                    pass
                node.update_neighbors(self.grid, allow_diagonal=diagonal, robot_size=self.robot_size)
        
        self.redraw()
        
        result = algorithm(self.canvas, self.grid, self.start, self.end,
                   allow_diagonal=diagonal,
                   robot_size=self.robot_size,
                   draw_callback=self.redraw)
        
        self.metrics_history.append(result)
        self.update_metrics_display(result)
        
        # Update comparison table
        self.update_comparison_table(result)
        self.previous_run = result
        
        if not result['success']:
            print("No path found!")
        else:
            print(f"Path found! Length: {result['path_length']:.2f}, Nodes explored: {result['nodes_explored']}")
            
            # Animate robot along the path if we have custom robot image
            if result.get('path_nodes') and self.use_custom_robot and self.robot_photo:
                self.root.after(500, lambda: self.animate_robot_on_path(result['path_nodes']))
        
        # Redraw to restore robot/goal images after path drawing
        self.redraw()
        self.running = False
    
    def toggle_robot(self, event=None):
        self.robot_size = 2 if self.robot_size == 1 else (3 if self.robot_size == 2 else 1)
        self.robot_label.configure(text=f"Model Size: {self.robot_size}x{self.robot_size}")
        
        # Resize robot image if using custom theme
        if self.use_custom_robot and self.robot_image:
            new_size = int(CELL_SIZE * self.robot_size * 0.8)
            resized_img = self.robot_image.resize((new_size, new_size), Image.Resampling.LANCZOS)
            self.robot_photo = ImageTk.PhotoImage(resized_img)

        # Resize goal image to match robot size
        if self.use_custom_goal and self.goal_image:
            goal_size = int(CELL_SIZE * self.robot_size * 0.8)
            resized_goal = self.goal_image.resize((goal_size, goal_size), Image.Resampling.LANCZOS)
            self.goal_photo = ImageTk.PhotoImage(resized_goal)
        
        self.redraw()
        print(f"Robot size: {self.robot_size}x{self.robot_size}")
    
    def clear_grid(self, event=None):
        # Stop any ongoing animation
        if hasattr(self, 'animation_index'):
            delattr(self, 'animation_index')
        if hasattr(self, 'path_nodes'):
            delattr(self, 'path_nodes')
        
        self.grid = make_grid(ROWS)
        self.start = None
        self.end = None
        self.robot_size = 1
        self.robot_label.configure(text=f"Model Size: {self.robot_size}x{self.robot_size}")
        self.update_metrics_display()
        self.redraw()
    
    def load_robot_image(self):
        """Load a custom robot image"""
        file_path = filedialog.askopenfilename(
            title="Select Robot Image",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                # Load and resize image
                img = Image.open(file_path)
                size = int(CELL_SIZE * self.robot_size * 0.8)
                img = img.resize((size, size), Image.Resampling.LANCZOS)
                self.robot_image = img
                self.robot_photo = ImageTk.PhotoImage(img)
                self.use_custom_robot = True
                self.redraw()
                print(f"Robot image loaded: {file_path}")
            except Exception as e:
                print(f"Error loading robot image: {e}")
    
    def use_default_robot(self):
        """Switch back to default drawn robot"""
        self.use_custom_robot = False
        self.redraw()
        print("Using default robot")
    
    def load_obstacle_image(self):
        """Load a custom obstacle/wall image"""
        file_path = filedialog.askopenfilename(
            title="Select Obstacle Image",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                # Load and resize image
                img = Image.open(file_path)
                size = int(CELL_SIZE * 0.9)
                img = img.resize((size, size), Image.Resampling.LANCZOS)
                self.obstacle_image = img
                self.obstacle_photo = ImageTk.PhotoImage(img)
                self.use_custom_obstacle = True
                self.redraw()
                print(f"Obstacle image loaded: {file_path}")
            except Exception as e:
                print(f"Error loading obstacle image: {e}")
    
    def use_default_obstacle(self):
        """Switch back to default black walls"""
        self.use_custom_obstacle = False
        self.redraw()
        print("Using default walls")
    
    def switch_theme_by_key(self, theme_key):
        """Professional theme switcher with algorithm-specific behavior and dynamic re-coloring"""
        global BACKGROUND_COLOR, PATH_COLOR, OPEN_COLOR, CLOSED_COLOR, WEIGHT_COLOR, WEIGHT_VALUE
        
        theme = self.theme_manager.get_theme(theme_key)
        if not theme:
            print(f"Theme '{theme_key}' not found!")
            return
        
        self.current_theme_key = theme_key
        theme_colors = THEME_CONFIG.get(theme_key, THEME_CONFIG["rabbit"])
        
        print(f"\n{'='*50}")
        print(f"SWITCHING TO: {theme.name}")
        print(f"{theme.description}")
        print(f"{'='*50}")
        
        # Apply theme-specific algorithm parameters
        self.robot_size = theme.robot_size
        self.robot_label.configure(text=f"Model Size: {self.robot_size}×{self.robot_size}")
        
        # Apply visual parameters from theme_manager
        BACKGROUND_COLOR = theme.background
        PATH_COLOR = theme.path_color
        OPEN_COLOR = theme.open_color
        CLOSED_COLOR = theme.closed_color
        WEIGHT_COLOR = theme_colors["weight"]
        WEIGHT_VALUE = theme.weight_value if theme.allow_weights else 5
        
        # Set ghost path color based on theme background brightness
        # Dark backgrounds need light ghost, light backgrounds need dark ghost
        if theme_key == 'rabbit':
            self.ghost_color = "#909090"  # Medium grey for light background
        elif theme_key == 'space':
            self.ghost_color = "#6080a0"  # Blue-tinted light grey for dark space
        elif theme_key == 'escape':
            self.ghost_color = "#c0a080"  # Warm light grey for dungeon
        else:
            self.ghost_color = "#808080"  # Default medium grey
        
        # Apply THEME_CONFIG colors to existing grid (re-coloring maze/obstacles)
        for row in self.grid:
            for node in row:
                if node.is_barrier():
                    # Re-color barriers to match new theme
                    node.color = theme_colors["obstacle"]
                elif node.is_weight():
                    # Weights remain but will be drawn with new theme color
                    pass
        
        print(f"Algorithm Config:")
        print(f"   - Robot Size: {theme.robot_size}×{theme.robot_size}")
        print(f"   - Weights Enabled: {theme.allow_weights}")
        print(f"   - Weight Cost: {theme.weight_value}×")
        print(f"Visual Config:")
        print(f"   - Background: {theme_colors['canvas_bg']}")
        print(f"   - Grid Lines: {theme_colors['grid_line']}")
        print(f"   - Obstacles: {theme_colors['obstacle']}")
        print(f"   - Path: {theme_colors['path']}")
        
        # Update canvas background
        self.canvas.config(bg=BACKGROUND_COLOR)

        if hasattr(self, "weight_info_label"):
            self.weight_info_label.configure(text=f"Cost: {WEIGHT_VALUE}×")
        
        # Update theme info label
        info_text = f"{theme.name}\n{theme.description}\nModel: {theme.robot_size}×{theme.robot_size} | Weight: {theme.weight_value}×"
        self.theme_info_label.configure(text=info_text)
        
        # Load theme assets
        robot_img, obstacle_img, goal_img = self.theme_manager.load_assets(theme_key, CELL_SIZE, theme.robot_size)
        
        if robot_img:
            self.robot_image = robot_img
            self.robot_photo = ImageTk.PhotoImage(robot_img)
            self.use_custom_robot = True
            print(f"Robot image loaded")
        else:
            self.use_custom_robot = False
            print(f"Using default robot graphics")
        
        if obstacle_img:
            self.obstacle_image = obstacle_img
            self.obstacle_photo = ImageTk.PhotoImage(obstacle_img)
            self.use_custom_obstacle = True
            print(f"Obstacle image loaded")
        else:
            self.use_custom_obstacle = False
            print(f"Using default obstacle graphics")
        
        if goal_img:
            self.goal_image = goal_img
            self.goal_photo = ImageTk.PhotoImage(goal_img)
            self.use_custom_goal = True
            print(f"Goal image loaded")
        else:
            self.use_custom_goal = False
            print(f"Using default goal graphics")
        
        print(f"{'='*50}\n")
        
        self.redraw()


if __name__ == "__main__":
    root = tk.Tk()
    app = AStar_App(root)
    # Load default theme
    app.switch_theme_by_key("rabbit")
    root.mainloop()
