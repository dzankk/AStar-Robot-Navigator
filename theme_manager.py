"""
Professional Theme Manager for A* Pathfinding Visualization
Handles theme switching with algorithm-specific behaviors
"""

import os
from pathlib import Path
from PIL import Image

class ThemeConfig:
    """Configuration for a single theme with algorithm parameters"""
    def __init__(self, name, description, robot_size, allow_weights, weight_value, 
                 background, path_color, open_color, closed_color, weight_color,
                 robot_image=None, obstacle_image=None, goal_image=None):
        self.name = name
        self.description = description
        
        # Algorithm parameters
        self.robot_size = robot_size
        self.allow_weights = allow_weights
        self.weight_value = weight_value
        
        # Visual parameters
        self.background = background
        self.path_color = path_color
        self.open_color = open_color
        self.closed_color = closed_color
        self.weight_color = weight_color
        
        # Asset paths
        self.robot_image = robot_image
        self.obstacle_image = obstacle_image
        self.goal_image = goal_image


class ThemeManager:
    """Manages themes and their assets with algorithm-specific behaviors"""
    
    def __init__(self, assets_dir):
        self.assets_dir = Path(assets_dir)
        self.current_theme = None
        self.themes = self._initialize_themes()
        
    def _initialize_themes(self):
        """Initialize all theme configurations"""
        themes = {}
        
        # Theme 1: Carrot Hunt - Standard A* (1x1, uniform cost)
        themes['rabbit'] = ThemeConfig(
            name="Carrot Hunt",
            description="Standard A* with 1×1 point robot, uniform cost=1",
            robot_size=1,
            allow_weights=False,
            weight_value=1,
            background="#f0e6d2",
            path_color="#27ae60",
            open_color="rgba(46, 204, 113, 0.3)",
            closed_color="rgba(231, 76, 60, 0.3)",
            weight_color="#e74c3c",
            robot_image=self.assets_dir / "rabbit" / "robot.png",
            obstacle_image=self.assets_dir / "rabbit" / "obstacle.png",
            goal_image=self.assets_dir / "rabbit" / "goal.png"
        )
        
        # Theme 2: Dungeon Escape - Square Robot (2x2 footprint)
        themes['space'] = ThemeConfig(
            name="Dungeon Escape",
            description="2×2 footprint robot - all 4 cells must be clear",
            robot_size=2,
            allow_weights=False,
            weight_value=1,
            background="#0a0e27",
            path_color="#00ffff",
            open_color="rgba(0, 255, 255, 0.3)",
            closed_color="rgba(255, 100, 100, 0.3)",
            weight_color="#ff6464",
            robot_image=self.assets_dir / "space" / "robot.png",
            obstacle_image=self.assets_dir / "space" / "obstacle.png",
            goal_image=self.assets_dir / "space" / "goal.png"
        )
        
        # Theme 3: Obstacle Course - Weighted Terrain (high cost zones)
        themes['escape'] = ThemeConfig(
            name="Obstacle Course",
            description="Large square robot - 3×3 footprint validation with weighted terrain",
            robot_size=3,
            allow_weights=True,
            weight_value=5,
            background="#7a6a5a",
            path_color="#FFD700",
            open_color="rgba(255, 215, 0, 0.3)",
            closed_color="rgba(220, 20, 60, 0.3)",
            weight_color="#DC143C",
            robot_image=self.assets_dir / "escape" / "robot.png",
            obstacle_image=self.assets_dir / "escape" / "obstacle.png",
            goal_image=self.assets_dir / "escape" / "goal.png"
        )
        
        return themes
    
    def get_theme(self, theme_key):
        """Get theme configuration by key"""
        return self.themes.get(theme_key)
    
    def load_assets(self, theme_key, cell_size, robot_size_override=None):
        """Load and resize image assets for a theme"""
        theme = self.themes.get(theme_key)
        if not theme:
            return None, None, None
        
        robot_size = robot_size_override or theme.robot_size
        assets = {}
        
        # Load robot image
        if theme.robot_image and theme.robot_image.exists():
            try:
                img = Image.open(theme.robot_image)
                size = int(cell_size * robot_size * 0.8)
                img = img.resize((size, size), Image.Resampling.LANCZOS)
                assets['robot'] = img
            except Exception as e:
                print(f"Error loading robot image: {e}")
                assets['robot'] = None
        else:
            assets['robot'] = None
        
        # Load obstacle image
        if theme.obstacle_image and theme.obstacle_image.exists():
            try:
                img = Image.open(theme.obstacle_image)
                size = int(cell_size * 0.9)
                img = img.resize((size, size), Image.Resampling.LANCZOS)
                assets['obstacle'] = img
            except Exception as e:
                print(f"Error loading obstacle image: {e}")
                assets['obstacle'] = None
        else:
            assets['obstacle'] = None
        
        # Load goal image
        if theme.goal_image and theme.goal_image.exists():
            try:
                img = Image.open(theme.goal_image)
                size = int(cell_size * robot_size * 0.8)
                img = img.resize((size, size), Image.Resampling.LANCZOS)
                assets['goal'] = img
            except Exception as e:
                print(f"Error loading goal image: {e}")
                assets['goal'] = None
        else:
            assets['goal'] = None
        
        return assets.get('robot'), assets.get('obstacle'), assets.get('goal')
    
    def get_theme_names(self):
        """Get list of theme keys"""
        return list(self.themes.keys())
    
    def get_theme_display_name(self, theme_key):
        """Get display name for theme"""
        theme = self.themes.get(theme_key)
        return theme.name if theme else "Unknown"
