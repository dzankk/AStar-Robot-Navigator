# Dungeon Escape Theme

## Overview
An immersive escape room scenario where the robot is a prisoner attempting to escape a high-security dungeon while avoiding guard zones.

## Theme Colors
- **Background**: Dark Grey (#2c3e50) - Creates a dungeon atmosphere
- **Guard Zones**: Semi-transparent Red (#E74C3C) - High-security areas with weight: 15
- **Escape Path**: Electric Blue (#00d4ff) - The computed escape route
- **Walls**: Dark stone/prison walls

## Image Files Required
Place PNG files in this directory:

1. **robot.png** (128x128)
   - A prisoner/escapee character
   - Should have a recognizable escape/movement pose
   - Suggestion: Orange prison clothing, scared expression

2. **obstacle.png** (64x64)
   - Prison walls or stone barriers
   - Can be a dark grey/black texture
   - Suggestion: Stone wall pattern or prison cell bars

3. **goal.png** (64x64)
   - Freedom/exit symbol
   - Suggestion: Door, exit sign, freedom symbol, or light

## Gameplay
- Click to place the START (escapee position)
- Click to place the END (exit/freedom location)
- **Shift+Click or Shift+Drag** to paint guard zones (red areas with weight 15)
- Drag without Shift to paint walls
- Right-click to erase
- Run pathfinding algorithm
- The algorithm will avoid guard zones when possible due to high weight cost

## Story Context
"A prisoner must escape the dungeon by finding a path to freedom while avoiding areas monitored by heavy guard presence. The guards patrol high-security zones (shown in red), making those routes much more dangerous. The algorithm will seek the safest escape route, preferring longer paths through unguarded areas over risky passages through guard zones."
