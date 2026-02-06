"""
Theme Configuration for A* Pathfinding Visualization
Each theme can have robot and obstacle images
"""

import os
from pathlib import Path

# Get themes directory
THEMES_DIR = Path(__file__).parent

# Available themes
THEMES = {
    "default": {
        "name": "Default",
        "description": "Classic drawn style",
        "robot_image": None,  # Uses default drawn robot
        "obstacle_image": None,  # Uses default black walls
        "goal_image": None,  # Uses default flag
        "color_scheme": "default"
    },
    "rabbit": {
        "name": "🐰 Rabbit & Carrots",
        "description": "Cute rabbit collecting carrots!",
        "robot_image": os.path.join(THEMES_DIR, "rabbit", "robot.png"),
        "obstacle_image": os.path.join(THEMES_DIR, "rabbit", "obstacle.png"),
        "goal_image": os.path.join(THEMES_DIR, "rabbit", "goal.png"),
        "color_scheme": "rabbit",
        "background": "#f0e6d2",
        "path_color": "#27ae60"
    },
    "space": {
        "name": "🚀 Space Adventure",
        "description": "Spaceship collecting stars",
        "robot_image": os.path.join(THEMES_DIR, "space", "robot.png"),
        "obstacle_image": os.path.join(THEMES_DIR, "space", "obstacle.png"),
        "goal_image": os.path.join(THEMES_DIR, "space", "goal.png"),
        "color_scheme": "space",
        "background": "#0a0e27",
        "path_color": "#00ffff"
    },
    "dungeon": {
        "name": "🔐 Dungeon Escape",
        "description": "Escapee avoiding high-security guard zones",
        "robot_image": os.path.join(THEMES_DIR, "dungeon", "robot.png"),
        "obstacle_image": os.path.join(THEMES_DIR, "dungeon", "obstacle.png"),
        "goal_image": os.path.join(THEMES_DIR, "dungeon", "goal.png"),
        "color_scheme": "dungeon",
        "background": "#2c3e50",
        "path_color": "#00d4ff",
        "weight_color": "#e74c3c",
        "weight_value": 15
    },
}


def get_theme(theme_name):
    """Get theme configuration"""
    return THEMES.get(theme_name, THEMES["default"])


def get_theme_images(theme_name):
    """Load theme images if they exist"""
    theme = get_theme(theme_name)
    robot_img = None
    obstacle_img = None
    goal_img = None
    
    # Try to load robot image
    if theme["robot_image"] and os.path.exists(theme["robot_image"]):
        try:
            from PIL import Image
            robot_img = Image.open(theme["robot_image"])
        except:
            pass
    
    # Try to load obstacle image
    if theme["obstacle_image"] and os.path.exists(theme["obstacle_image"]):
        try:
            from PIL import Image
            obstacle_img = Image.open(theme["obstacle_image"])
        except:
            pass
    
    # Try to load goal image
    if theme["goal_image"] and os.path.exists(theme["goal_image"]):
        try:
            from PIL import Image
            goal_img = Image.open(theme["goal_image"])
        except:
            pass
    
    return robot_img, obstacle_img, goal_img


def list_themes():
    """Return list of available themes"""
    return list(THEMES.keys())
