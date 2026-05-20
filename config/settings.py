# config/settings.py

# Screen dimensions = internal simulation resolution
# The game renders at this size then scales to fit the window
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 960

# Simulation tick rate
SIM_FPS = 60
FIXED_DT = 1.0 / SIM_FPS

# Render FPS — uncapped by default
RENDER_FPS = 1000000

# Fallback background color
BACKGROUND_COLOR = (30, 30, 30)